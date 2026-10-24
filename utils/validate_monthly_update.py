"""Check that a monthly PR only adds that month's data with plausible record counts."""

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path

VERSION_FILE = "src/economy_watchers_survey/version.py"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def previous_months(year, month, count=6):
    index = year * 12 + month - 1
    return [
        f"{(index - offset) // 12:04d}{(index - offset) % 12 + 1:02d}"
        for offset in range(1, count + 1)
    ]


def record_count(content):
    rows = json.loads(content)
    if not isinstance(rows, list) or not rows:
        raise ValueError("Expected a nonempty JSON array")
    return len(rows)


def check_count(count, history):
    median = statistics.median(history)
    # Compare scaled values so the inclusive 90-110% bounds stay exact.
    if not 9 * median <= 10 * count <= 11 * median:
        raise ValueError(f"{count} records outside 90-110% of the median {median}")
    return {"count": count, "median": median}


def check_versions(repo, base, head, version):
    diff = git(repo, "diff", "-U0", base, head, "--", "pyproject.toml")
    lines = [
        line
        for line in diff.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    if len(lines) != 2 or not lines[0].startswith("-version = "):
        raise ValueError("pyproject.toml may only change its version")
    match = re.fullmatch(r'\+version = "([0-9.]+)"', lines[1])
    # Poetry may normalize 2026.09.0 to 2026.9.0, so compare the numbers.
    if not match or [int(n) for n in match[1].split(".")] != [
        int(n) for n in version.split(".")
    ]:
        raise ValueError("pyproject.toml version does not match the release")
    if git(repo, "show", f"{head}:{VERSION_FILE}") != f'__version__ = "{version}"\n':
        raise ValueError("version.py does not match the release")


def validate(repo, base, head, version):
    match = re.fullmatch(r"(\d{4})\.(0[1-9]|1[0-2])\.0", version)
    if not match:
        raise ValueError(f"Expected YYYY.MM.0, got {version!r}")
    year, month = match[1], match[2]
    year_month = year + month
    # Diff from the PR's branch point so later commits on main are not counted.
    base = git(repo, "merge-base", base, head).strip()
    data_files = [
        f"data/watcher/{year}/{year_month}_watcher4.csv",
        f"data/watcher/{year}/{year_month}_watcher5.csv",
        f"data/current/{year_month}.json",
        f"data/future/{year_month}.json",
    ]
    expected = {path: "A" for path in data_files}
    expected.update({"pyproject.toml": "M", VERSION_FILE: "M"})
    diff = git(repo, "diff", "--name-status", "--no-renames", base, head)
    changes = {}
    for line in diff.splitlines():
        status, path = line.split("\t")
        changes[path] = status
    if changes != expected:
        unexpected = sorted(set(changes.items()) ^ set(expected.items()))
        raise ValueError(f"Unexpected file changes: {unexpected}")
    for path in data_files[:2]:
        if git(repo, "cat-file", "-s", f"{head}:{path}").strip() == "0":
            raise ValueError(f"Empty data file: {path}")
    check_versions(repo, base, head, version)

    result = {"version": version, "base": base}
    for kind in ("current", "future"):
        history = [
            record_count(git(repo, "show", f"{base}:data/{kind}/{previous}.json"))
            for previous in previous_months(int(year), int(month))
        ]
        count = record_count(git(repo, "show", f"{head}:data/{kind}/{year_month}.json"))
        try:
            result[kind] = check_count(count, history)
        except ValueError as error:
            raise ValueError(f"{kind}: {error}") from error
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.repo, args.base, args.head, args.version), indent=2))


if __name__ == "__main__":
    main()
