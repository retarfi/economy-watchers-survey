"""Check that the Hugging Face tag holds the released version and month."""

import argparse
import json
from pathlib import Path

REPO_ID = "retarfi/economy-watchers-survey"


def published_count(path, year_month):
    with open(path, encoding="utf-8") as stream:
        return sum(json.loads(line)["year-month"] == year_month for line in stream)


def verify(snapshot, source, version):
    year, month, _ = version.split(".")
    year_month = year + month
    published_version = (snapshot / "version.py").read_text(encoding="utf-8")
    if published_version != f'__version__ = "{version}"\n':
        raise ValueError("Published version.py does not match the release")
    counts = {}
    for kind in ("current", "future"):
        expected = len(
            json.loads(
                (source / "data" / kind / f"{year_month}.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        actual = sum(
            published_count(path, year_month)
            for path in (snapshot / kind).glob("*.jsonl")
        )
        if actual != expected:
            raise ValueError(f"{kind}: published {actual} records, expected {expected}")
        counts[kind] = actual
    return counts


def main():
    # Imported here so the tests only need the standard library.
    from huggingface_hub import snapshot_download

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    # Downloading by tag also fails when the tag was not created.
    snapshot = snapshot_download(
        REPO_ID,
        repo_type="dataset",
        revision=args.version,
        allow_patterns=["version.py", "current/*.jsonl", "future/*.jsonl"],
    )
    print(json.dumps(verify(Path(snapshot), Path("."), args.version)))


if __name__ == "__main__":
    main()
