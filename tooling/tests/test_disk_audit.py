"""Metadata-only storage scanning with disposable local fixtures."""
import importlib.util
from pathlib import Path
import os
import tempfile
import unittest
from unittest import mock

TOOLING = Path(__file__).absolute().parents[1]
SCRIPT = TOOLING / "src/local_scripts/disk_audit.py"


class DiskAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TOOLING / "tests")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def module(self):
        self.assertTrue(SCRIPT.is_file(), "Metadata-only audit is not implemented")
        spec = importlib.util.spec_from_file_location("disk_audit", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_never_follows_symlinks_or_cloud_paths_or_reads_file_contents(self):
        scan = self.root / "scan"
        scan.mkdir()
        (scan / "local.bin").write_bytes(b"x" * 100)
        cloud = scan / "Library/CloudStorage"
        cloud.mkdir(parents=True)
        (cloud / "private.bin").write_bytes(b"x" * 900)
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "large.bin").write_bytes(b"x" * 800)
        (scan / "link").symlink_to(outside, target_is_directory=True)
        module = self.module()
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("File content read")):
            result = module.measure(scan)
        self.assertEqual(result["logical_bytes"], 100)
        self.assertEqual(result["files"], 1)
        self.assertGreaterEqual(result["skipped"], 2)

    def test_hardlinked_files_are_counted_once_and_allocated_bytes_are_labelled(self):
        original = self.root / "a"
        original.write_bytes(b"x" * 5000)
        os.link(original, self.root / "b")
        result = self.module().measure(self.root)
        self.assertEqual(result["logical_bytes"], 5000)
        self.assertEqual(result["allocated_bytes"], original.stat().st_blocks * 512)

    def test_largest_projects_are_sorted_and_include_real_directories_only(self):
        sites = self.root / "sites"
        sites.mkdir()
        for name, size in (("small", 10), ("large", 9000)):
            (sites / name).mkdir()
            (sites / name / "file").write_bytes(b"x" * size)
        (sites / "cloud Dropbox").mkdir()
        (sites / "alias").symlink_to(sites / "large", target_is_directory=True)
        projects = self.module().project_usage(sites)
        self.assertEqual([p["name"] for p in projects], ["large", "small"])
        self.assertEqual(projects[0]["logical_bytes"], 9000)

    def test_missing_or_unreadable_directory_is_partial_without_raw_errors(self):
        module = self.module()
        result = module.measure(self.root / "absent")
        self.assertTrue(result["partial"])
        self.assertEqual(result["errors"], 1)
        self.assertNotIn("exception", result)
        with mock.patch.object(module.os, "scandir", side_effect=PermissionError("private payload")):
            denied = module.measure(self.root)
        self.assertTrue(denied["partial"])
        self.assertEqual(denied["errors"], 1)
        self.assertNotIn("private payload", str(denied))

    def test_credential_stores_and_mounted_roots_are_excluded(self):
        module = self.module()
        for path in ("Library/Mobile Documents", "Library/CloudStorage", ".ssh", ".aws", "Library/Keychains", "Volumes/work", "Box", "OneDrive", "Dropbox"):
            self.assertTrue(module.excluded(Path(path)), path)

    def test_symlink_in_root_components_is_rejected(self):
        module = self.module()
        real = self.root / "real"
        real.mkdir()
        (real / "inside").mkdir()
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        result = module.measure(alias / "inside")
        self.assertTrue(result["partial"])
        self.assertEqual(result["files"], 0)


if __name__ == "__main__":
    unittest.main()
