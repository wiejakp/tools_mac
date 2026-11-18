"""Portable checkout contracts; never invoke real cleanup or network mounts."""
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = next(p for p in Path(__file__).absolute().parents if (p / "Makefile").is_file())


class ToolingMigrationTests(unittest.TestCase):
    def test_tools_live_in_tooling_and_run_from_another_working_directory(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as cwd:
            for name in ("clear-cache.sh", "clear-logs.sh", "mount.sh", "agent-setup.sh", "disk-usage.sh"):
                with self.subTest(name=name):
                    entry = ROOT / "tooling" / name
                    self.assertTrue(entry.is_file(), str(entry))
                    result = subprocess.run([str(entry), "--help"], cwd=cwd,
                                            capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("usage:", result.stdout.lower())

    def test_root_make_targets_dispatch_to_tooling_without_cleanup_approval(self):
        for kind in ("cache", "logs"):
            result = subprocess.run(["make", "-n", "clear", kind], cwd=ROOT,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("tooling/clear-" + kind + ".sh", result.stdout)
            self.assertNotIn("--yes", result.stdout)


if __name__ == "__main__":
    unittest.main()
