import json
import tempfile
import unittest
from pathlib import Path

from utils.verify_release import verify

VERSION = "2026.09.0"


class ReleaseVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.snapshot = self.root / "hf"
        self.write("hf/version.py", f'__version__ = "{VERSION}"\n')
        for kind in ("current", "future"):
            self.write(f"data/{kind}/202609.json", "[{}, {}]")
            self.write(f"hf/{kind}/train.jsonl", '{"year-month": "202608"}\n')
            self.write(f"hf/{kind}/test.jsonl", '{"year-month": "202609"}\n' * 2)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_complete_release(self):
        self.assertEqual(
            verify(self.snapshot, self.root, VERSION), {"current": 2, "future": 2}
        )

    def test_old_version(self):
        self.write("hf/version.py", '__version__ = "2026.08.0"\n')
        with self.assertRaisesRegex(ValueError, "version"):
            verify(self.snapshot, self.root, VERSION)

    def test_target_month_missing(self):
        self.write("hf/future/test.jsonl", '{"year-month": "202608"}\n')
        with self.assertRaisesRegex(ValueError, "future"):
            verify(self.snapshot, self.root, VERSION)


if __name__ == "__main__":
    unittest.main()
