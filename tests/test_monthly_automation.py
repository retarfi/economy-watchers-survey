import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from utils.validate_monthly_update import (
    check_count,
    previous_months,
    record_count,
    validate,
)

VERSION = "2026.09.0"
PYPROJECT = '[tool.poetry]\nname = "test"\nversion = "{}"\n'


class CountTests(unittest.TestCase):
    def test_inclusive_boundaries(self):
        for count in (90, 100, 110):
            self.assertEqual(check_count(count, [100] * 6)["count"], count)
        for count in (89, 111):
            with self.subTest(count=count), self.assertRaises(ValueError):
                check_count(count, [100] * 6)

    def test_half_integer_median(self):
        history = [100, 100, 100, 101, 101, 101]
        for count in (91, 110):
            check_count(count, history)
        for count in (90, 111):
            with self.subTest(count=count), self.assertRaises(ValueError):
                check_count(count, history)

    def test_json_count(self):
        self.assertEqual(record_count("[{}, {}]"), 2)
        for content in ("[]", "{}", "null"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                record_count(content)

    def test_previous_months_cross_year(self):
        self.assertEqual(
            previous_months(2026, 1),
            ["202512", "202511", "202510", "202509", "202508", "202507"],
        )


class MonthlyDiffTests(unittest.TestCase):
    """Commits are created only inside disposable fixture repositories."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.write("pyproject.toml", PYPROJECT.format("2026.08.0"))
        self.write(
            "src/economy_watchers_survey/version.py", '__version__ = "2026.08.0"\n'
        )
        for kind in ("current", "future"):
            for month in previous_months(2026, 9):
                self.write(f"data/{kind}/{month}.json", json.dumps([{}] * 100))
        self.base = self.commit()
        for kind in ("current", "future"):
            self.write(f"data/{kind}/202609.json", json.dumps([{}] * 100))
        for number in (4, 5):
            self.write(f"data/watcher/2026/202609_watcher{number}.csv", "csv\n")
        self.write("pyproject.toml", PYPROJECT.format(VERSION))
        self.write(
            "src/economy_watchers_survey/version.py", f'__version__ = "{VERSION}"\n'
        )

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self):
        self.git("add", "-A")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        )
        return self.git("rev-parse", "HEAD")

    def result(self):
        return validate(self.root, self.base, self.commit(), VERSION)

    def test_complete_monthly_update(self):
        result = self.result()
        self.assertEqual(result["current"], {"count": 100, "median": 100})
        self.assertEqual(result["future"], {"count": 100, "median": 100})

    def test_normalized_poetry_version(self):
        self.write("pyproject.toml", PYPROJECT.format("2026.9.0"))
        self.result()

    def assert_unexpected_changes(self):
        with self.assertRaisesRegex(ValueError, "Unexpected file changes"):
            self.result()

    def test_code_change_rejected(self):
        self.write("src/unexpected.py", "print('unrelated')\n")
        self.assert_unexpected_changes()

    def test_historical_change_rejected(self):
        self.write("data/current/202608.json", json.dumps([{}] * 101))
        self.assert_unexpected_changes()

    def test_extra_month_rejected(self):
        self.write("data/future/202610.json", "[{}]")
        self.assert_unexpected_changes()

    def test_missing_monthly_file_rejected(self):
        (self.root / "data/future/202609.json").unlink()
        self.assert_unexpected_changes()

    def test_missing_version_bump_rejected(self):
        self.write(
            "src/economy_watchers_survey/version.py", '__version__ = "2026.08.0"\n'
        )
        self.assert_unexpected_changes()

    def test_dependency_change_rejected(self):
        self.write(
            "pyproject.toml",
            PYPROJECT.format(VERSION) + '[tool.poetry.dependencies]\nnew = "*"\n',
        )
        with self.assertRaisesRegex(ValueError, "only change its version"):
            self.result()

    def test_empty_csv_rejected(self):
        self.write("data/watcher/2026/202609_watcher4.csv", "")
        with self.assertRaisesRegex(ValueError, "Empty data file"):
            self.result()

    def test_future_count_is_checked_independently(self):
        self.write("data/future/202609.json", json.dumps([{}] * 111))
        with self.assertRaisesRegex(ValueError, "future"):
            self.result()


if __name__ == "__main__":
    unittest.main()
