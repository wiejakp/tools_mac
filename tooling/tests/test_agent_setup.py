"""Agent setup tests use disposable local fixtures, never the real agent home."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
import io
from types import SimpleNamespace

ROOT = Path(__file__).absolute().parents[1]
MODULE = ROOT / "src/local_scripts/agent_setup.py"


class PluginRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".agent-setup-test-", dir=ROOT / "tests")
        self.base = Path(self.temp.name)
        self.plugin = self.base / "plugin"
        self.bin = self.plugin / "node_modules/.bin"
        self.bin.mkdir(parents=True)
        self.target = self.plugin / "node_modules/tool/cli.sh"
        self.target.parent.mkdir()
        self.target.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n', encoding="utf-8")
        self.target.chmod(0o755)
        self.link = self.bin / "tool"
        self.link.symlink_to("../tool/cli.sh")
        self.backup = self.base / "backups"

    def tearDown(self):
        self.temp.cleanup()

    def repair(self, apply=False):
        self.assertTrue(MODULE.is_file(), "Repeatable safe plugin repair is missing")
        spec = importlib.util.spec_from_file_location("agent_setup", MODULE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module.repair_plugin(self.plugin, self.backup, apply)

    def test_preview_leaves_plugin_and_backup_untouched(self):
        changes = self.repair()
        self.assertEqual(len(changes), 1)
        self.assertTrue(self.link.is_symlink())
        self.assertFalse(self.backup.exists())

    def test_forwarder_preserves_arguments_and_original_target(self):
        original = self.target.read_bytes()
        self.repair(apply=True)
        self.assertFalse(self.link.is_symlink())
        result = subprocess.run([str(self.link), "two words", "$(no-execution)", ""],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, "two words\n$(no-execution)\n\n")
        self.assertEqual(self.target.read_bytes(), original)
        saved = list(self.backup.glob("*.json"))
        self.assertEqual(len(saved), 1)
        record = json.loads(saved[0].read_text())
        self.assertEqual(record["links"][0]["target"], "../tool/cli.sh")

    def test_second_repair_does_not_rewrite_or_create_backup(self):
        self.repair(apply=True)
        before = self.link.stat().st_mtime_ns
        self.assertEqual(self.repair(apply=True), [])
        self.assertEqual(self.link.stat().st_mtime_ns, before)
        self.assertEqual(len(list(self.backup.glob("*.json"))), 1)

    def test_escaping_link_rejects_entire_repair_before_mutation(self):
        external = self.base / "outside"
        external.write_text("must stay untouched")
        (self.bin / "escape").symlink_to(external)
        with self.assertRaisesRegex(ValueError, "outside"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())
        self.assertFalse(self.backup.exists())

    def test_broken_link_rejected_without_mutation(self):
        (self.bin / "broken").symlink_to("../missing")
        with self.assertRaisesRegex(ValueError, "missing|broken"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())

    def test_link_outside_npm_bin_is_not_rewritten(self):
        (self.plugin / "unexpected").symlink_to("node_modules/tool/cli.sh")
        with self.assertRaisesRegex(ValueError, "unexpected|npm"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())

    def test_symlink_plugin_root_is_rejected(self):
        alias = self.base / "alias"
        alias.symlink_to(self.plugin, target_is_directory=True)
        self.plugin = alias
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.repair(apply=True)

    def test_non_executable_target_is_rejected(self):
        self.target.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "executable"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())

    def test_absolute_internal_link_still_executes(self):
        self.link.unlink()
        self.link.symlink_to(self.target)
        self.repair(apply=True)
        result = subprocess.run([str(self.link), "argument"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "argument\n")

    def test_symlinked_plugin_ancestor_is_rejected(self):
        alias = self.base / "alias"
        alias.symlink_to(self.base, target_is_directory=True)
        self.plugin = alias / "plugin"
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())

    def test_symlinked_backup_directory_is_rejected(self):
        outside = self.base / "other-backups"
        outside.mkdir()
        self.backup.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.repair(apply=True)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(list(outside.iterdir()), [])


class LocalToolHealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".agent-health-test-", dir=ROOT / "tests")
        self.base = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location("agent_setup_health", MODULE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        events = ["PreToolUse", "PostToolUse", "SessionStart", "PreCompact", "UserPromptSubmit", "Stop"]
        self.hooks = [{"eventName": event, "enabled": True, "trustStatus": "trusted", "source": "user",
                       "command": "context-mode hook codex " + event.lower()} for event in events]
        self.servers = [
            {"name": "cce-other", "enabled": True, "transport": {"type": "stdio", "command": "wrong-cce",
                "args": ["serve", "--project-dir", str(self.base / "other")]}},
            {"name": "cce-current", "enabled": True, "transport": {"type": "stdio", "command": "/fixture/cce",
                "args": ["serve", "--project-dir", str(ROOT)]}},
            {"name": "context-mode", "enabled": True, "transport": {"type": "stdio", "command": "/fixture/context-mode", "args": []}},
        ]
        self.calls = []
        self.ctx_output = "42\n"
        self.ctx_search_error = None
        self.cce_status = "Index status: operational"
        self.skills = [{"name": name} for name in ["context-mode", "ctx-doctor", "ctx-index", "ctx-insight", "ctx-purge", "ctx-search", "ctx-stats", "ctx-upgrade"]]

    def tearDown(self):
        self.temp.cleanup()

    def fake_client(self, command, cwd, **kwargs):
        self.calls.append(list(command))
        test = self

        class Client:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def request(self, method, params):
                if method == "hooks/list":
                    return {"data": [{"cwd": str(ROOT), "hooks": test.hooks, "errors": []}]}
                if method == "skills/list":
                    return {"data": [{"cwd": str(ROOT), "skills": test.skills}]}
                name = params.get("name")
                if name == "ctx_search" and test.ctx_search_error:
                    return {"content": [{"type": "text", "text": test.ctx_search_error}], "isError": True}
                value = test.ctx_output if name == "ctx_execute" else test.cce_status if name == "index_status" else "local result"
                return {"content": [{"type": "text", "text": value}], "isError": False}
        return Client()

    def check(self):
        def run(command, **kwargs):
            if "rev-parse" in command: output = str(ROOT) + "\n"
            elif "mcp" in command: output = json.dumps(self.servers)
            else: output = "codex-cli test\n"
            return SimpleNamespace(returncode=0, stdout=output, stderr="")
        with mock.patch.object(self.module.shutil, "which", side_effect=lambda name: name), \
                mock.patch.object(self.module.subprocess, "run", side_effect=run), \
                mock.patch.object(self.module, "LocalJsonRpc", side_effect=self.fake_client):
            return self.module.check_agent_tools(ROOT)

    def test_health_proves_native_hooks_and_only_the_matching_local_servers(self):
        checks = self.check()
        self.assertTrue(checks and all(row["ok"] for row in checks), checks)
        self.assertTrue(any(command[0] == "/fixture/cce" for command in self.calls))
        self.assertFalse(any(command[0] == "wrong-cce" for command in self.calls))

    def test_health_rejects_untrusted_native_hooks(self):
        self.hooks[0]["trustStatus"] = "untrusted"
        self.assertTrue(any(not row["ok"] and "hook" in row["name"].lower() for row in self.check()))

    def test_health_rejects_missing_context_skills(self):
        self.skills = []
        self.assertTrue(any(not row["ok"] and "hook" in row["name"].lower() for row in self.check()))

    def test_health_rejects_an_unavailable_cce_index(self):
        self.cce_status = "Index has not been initialized"
        self.assertTrue(any(not row["ok"] and "CCE" in row["name"] for row in self.check()))

    def test_health_never_probes_remote_context_mode(self):
        self.servers[-1]["transport"] = {"type": "http", "url": "https://example.invalid"}
        self.assertTrue(any(not row["ok"] and "CTX" in row["name"] for row in self.check()))
        self.assertFalse(any(command[0] == "/fixture/context-mode" for command in self.calls))

    def test_health_rejects_remote_proxies_even_when_transport_is_stdio(self):
        self.servers[-1]["transport"] = {"type": "stdio", "command": "ssh", "args": ["host", "context-mode"]}
        self.assertTrue(any(not row["ok"] and "CTX" in row["name"] for row in self.check()))
        self.assertFalse(any(command[0] == "ssh" for command in self.calls))

    def test_health_does_not_borrow_another_projects_cce(self):
        self.servers.pop(1)
        self.assertTrue(any(not row["ok"] and "CCE" in row["name"] for row in self.check()))
        self.assertFalse(any(command[0] == "wrong-cce" for command in self.calls))

    def test_health_refuses_cloud_roots_before_any_subprocess(self):
        for folder in ("FileProvider", "Box"):
            with mock.patch.object(self.module.subprocess, "run", side_effect=AssertionError("Cloud path accessed")) as run:
                checks = self.module.check_agent_tools(self.base / folder)
            run.assert_not_called()
            self.assertTrue(checks and not checks[0]["ok"])

    def test_health_requires_execution_output_not_echoed_input(self):
        self.ctx_output = "console.log(6 * 7)\nfailed to execute"
        self.assertTrue(any(not row["ok"] and "CTX" in row["name"] for row in self.check()))

    def test_check_tools_returns_failure_without_mutating(self):
        out = io.StringIO()
        with mock.patch.object(self.module, "check_agent_tools", return_value=[{"ok": False, "name": "CTX", "detail": "unavailable"}]), redirect_stdout(out):
            self.assertEqual(self.module.main(["--check-tools"]), 1)
        self.assertIn("FAIL", out.getvalue())

    def test_empty_context_knowledge_base_is_a_reported_ready_state(self):
        for prefix in ("", "⚠️ context-mode outdated; update available\n\n"):
            self.ctx_search_error = prefix + "Knowledge base is empty — no content has been indexed yet."
            checks = self.check()
            self.assertTrue(all(row["ok"] for row in checks), checks)
            self.assertIn("empty", next(row["detail"] for row in checks if row["name"] == "Local CTX"))

    def test_unexpected_context_search_failure_keeps_its_diagnostic(self):
        self.ctx_search_error = "SQLite diagnostic failure"
        row = next(row for row in self.check() if row["name"] == "Local CTX")
        self.assertFalse(row["ok"])
        self.assertIn("SQLite diagnostic failure", row["detail"])

    def test_local_rpc_handles_notifications_and_closes_owned_process(self):
        script = self.base / "rpc fixture.py"
        script.write_text('''import sys,json,time
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m: continue
 if m['method']=='hang': time.sleep(10)
 print(json.dumps({'jsonrpc':'2.0','method':'notice','params':{}}),flush=True)
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':{'echo':m.get('params',{})}}),flush=True)
''')
        with self.module.LocalJsonRpc([sys.executable, "-u", str(script)], self.base, timeout=3) as client:
            self.assertEqual(client.request("echo", {"literal": "$(no execution)"})["echo"]["literal"], "$(no execution)")
            self.assertTrue(client.notifications)
            process = client.process
        self.assertIsNotNone(process.poll())

    def test_local_rpc_timeout_stops_owned_process(self):
        script = self.base / "hanging.py"
        script.write_text('''import sys,json,time
for line in sys.stdin:
 m=json.loads(line)
 if 'id' not in m: continue
 if m['method']=='hang': time.sleep(10)
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':{}}),flush=True)
''')
        with self.module.LocalJsonRpc([sys.executable, "-u", str(script)], self.base, timeout=3) as client:
            client.timeout = 0.05
            process = client.process
            with self.assertRaises((TimeoutError, ValueError)):
                client.request("hang", {})
        self.assertIsNotNone(process.poll())


class SharedSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".agent-setup-test-", dir=ROOT / "tests")
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.repo = self.base / "repo"
        self.original = self.home / ".codex/skills/example/SKILL.md"
        self.original.parent.mkdir(parents=True)
        self.original.write_text("Original skill\n")
        system = self.home / ".codex/skills/.system/internal"
        system.mkdir(parents=True)
        (system / "SKILL.md").write_text("Managed skill\n")
        helper = self.repo / ".agents/skills/mac-helper/SKILL.md"
        helper.parent.mkdir(parents=True)
        helper.write_text("Portable helper\n")
        instructions = self.repo / ".agents/skills/mac-helper/references/shared-instructions.md"
        instructions.parent.mkdir()
        instructions.write_text("Shared local agent guidance\n")
        (self.home / ".codex/AGENTS.md").write_text("Keep existing rules\n")

    def tearDown(self):
        self.temp.cleanup()

    def install(self, apply=False):
        spec = importlib.util.spec_from_file_location("agent_setup", MODULE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, "install_shared_skills"), "Shared skill installation is missing")
        return module.install_shared_skills(self.home, self.repo, apply)

    def test_preview_keeps_original_paths_and_contents(self):
        self.assertTrue(self.install())
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse(self.original.parent.is_symlink())
        self.assertEqual(self.original.read_text(), "Original skill\n")

    def test_agents_read_and_edit_the_same_skill(self):
        self.install(apply=True)
        shared = self.home / ".agents/skills/example/SKILL.md"
        self.assertTrue(self.original.parent.is_symlink())
        for agent in (".codex", ".claude", ".gemini"):
            candidate = self.home / agent / "skills/example/SKILL.md"
            self.assertTrue(os.path.samefile(candidate, shared))
        (self.home / ".claude/skills/example/SKILL.md").write_text("One shared update\n")
        self.assertEqual(self.original.read_text(), "One shared update\n")
        self.assertEqual((self.home / ".gemini/skills/example/SKILL.md").read_text(), "One shared update\n")
        self.assertFalse((self.home / ".codex/skills/.system").is_symlink())

    def test_repeated_install_does_not_duplicate_instructions_or_backups(self):
        self.install(apply=True)
        original = (self.home / ".codex/AGENTS.md").read_bytes()
        backups = list((self.home / ".agents/backups").iterdir())
        self.assertEqual(self.install(apply=True), [])
        self.assertEqual((self.home / ".codex/AGENTS.md").read_bytes(), original)
        self.assertEqual(list((self.home / ".agents/backups").iterdir()), backups)

    def test_conflicting_skill_rejects_before_any_change(self):
        conflict = self.home / ".agents/skills/example"
        conflict.mkdir(parents=True)
        (conflict / "SKILL.md").write_text("Other skill\n")
        with self.assertRaisesRegex(ValueError, "conflict|collision"):
            self.install(apply=True)
        self.assertFalse(self.original.parent.is_symlink())
        self.assertEqual((conflict / "SKILL.md").read_text(), "Other skill\n")
        self.assertFalse((self.home / ".agents/backups").exists())

    def test_existing_claude_skills_and_rules_are_preserved(self):
        other = self.home / ".claude/skills/second/SKILL.md"
        other.parent.mkdir(parents=True)
        other.write_text("Claude personal skill\n")
        rules = self.home / ".claude/CLAUDE.md"
        rules.write_text("Keep Claude rules\n")
        self.install(apply=True)
        self.assertEqual(other.read_text(), "Claude personal skill\n")
        self.assertEqual((self.home / ".agents/skills/second/SKILL.md").read_text(), "Claude personal skill\n")
        self.assertIn("Keep Claude rules", rules.read_text())
        self.assertIn("Keep existing rules", (self.home / ".codex/AGENTS.md").read_text())
        self.assertTrue((self.home / ".claude/skills/example/SKILL.md").is_file())
        self.assertTrue((self.home / ".claude/skills/mac-helper/SKILL.md").is_file())
        added = self.home / ".agents/skills/later/SKILL.md"
        added.parent.mkdir()
        added.write_text("Later shared skill\n")
        self.assertEqual((self.home / ".claude/skills/later/SKILL.md").read_text(), "Later shared skill\n")

    def test_inventory_does_not_follow_an_existing_report_link(self):
        spec = importlib.util.spec_from_file_location("agent_setup", MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, "write_inventory"), "Safe inventory write is missing")
        target = self.base / "unrelated.txt"
        target.write_text("Keep this data")
        report = self.repo / "report.json"
        report.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.write_inventory(report, {"fixture": True})
        self.assertEqual(target.read_text(), "Keep this data")

    def test_unexpected_agent_skill_root_symlink_is_not_followed(self):
        outside = self.base / "unapproved"
        outside.mkdir()
        (self.home / ".claude").mkdir()
        (self.home / ".claude/skills").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink|outside"):
            self.install(apply=True)
        self.assertFalse(self.original.parent.is_symlink())


if __name__ == "__main__":
    unittest.main()
