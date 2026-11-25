import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def cli(*args):
    return subprocess.run([sys.executable, "folder_weight.py", *args], text=True, capture_output=True)


class FolderWeightTests(unittest.TestCase):
    def test_hidden_files_links_totals_and_top_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            (nested / ".hidden").write_bytes(b"12345")
            os.link(nested / ".hidden", nested / "second")
            (root / "ignored-link").symlink_to(nested, target_is_directory=True)
            (root / "smaller").write_bytes(b"123")
            result = cli(root, "--top", "1", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "total_bytes": 13,
            "entries": [{"name": "nested", "bytes": 10}],
            "errors": [],
        })

    def test_missing_root_reports_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = cli(Path(tmp) / "missing")
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing", result.stderr)
