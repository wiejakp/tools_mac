"""Preview-first local agent setup; never reads credentials or downloads packages."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import select
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import List

TOOLING = Path(__file__).absolute().parents[2]
REPOSITORY = TOOLING.parent
CLOUD_NAMES = ("googledrive", "google drive", "onedrive", "sharepoint", "dropbox", "icloud", "fileprovider", "file provider")


def reject_cloud(path: Path) -> None:
    text = str(path).lower()
    if (any(name in text for name in CLOUD_NAMES) or "/library/cloudstorage" in text
            or "/library/mobile documents" in text or any(part.casefold() == "box" for part in path.parts)):
        raise ValueError("Cloud-backed paths are excluded")


def check_local_path(path: Path) -> None:
    """Reject symlink components before traversing approved repository/agent roots."""
    path = Path(os.path.abspath(path))
    reject_cloud(path)
    boundaries = [REPOSITORY] + [Path.home() / name for name in
                                  (".agents", ".codex", ".claude", ".gemini", ".cce")]
    matches = [root for root in boundaries if os.path.commonpath((str(path), str(root))) == str(root)]
    if not matches:
        raise ValueError("Path is outside the repository and approved agent configuration roots")
    root = max(matches, key=lambda candidate: len(candidate.parts))
    current = root
    for part in (None,) + path.relative_to(root).parts:
        if part is not None:
            current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            return
        if stat.S_ISLNK(mode):
            raise ValueError("Refusing a symlink in the path: " + str(current))


def local_target(link: Path, root: Path) -> Path:
    """Check each destination before following a link; never resolve outside root."""
    destination = Path(os.path.normpath(str(link.parent / os.readlink(link))))
    for _ in range(40):
        reject_cloud(destination)
        if os.path.commonpath((str(destination), str(root))) != str(root):
            raise ValueError("npm link points outside the plugin: " + str(link.relative_to(root)))
        current = root
        redirected = False
        parts = destination.relative_to(root).parts
        for index, part in enumerate(parts):
            current = current / part
            try:
                entry = current.lstat()
            except FileNotFoundError:
                raise ValueError("Missing or broken npm link: " + str(link.relative_to(root))) from None
            if stat.S_ISLNK(entry.st_mode):
                destination = Path(os.path.normpath(str(current.parent / os.readlink(current) / Path(*parts[index + 1:]))))
                redirected = True
                break
        if not redirected:
            return destination
    raise ValueError("npm link cycle: " + str(link.relative_to(root)))


def save_backup(directory: Path, name: str, data: dict) -> Path:
    check_local_path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = directory / (name + "-" + stamp + ".json")
    with output.open("x", encoding="utf-8") as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(data, stream, indent=2)
        stream.write("\n")
    return output


def repair_plugin(plugin: Path, backup: Path, apply: bool = False) -> List[str]:
    """Replace internal npm bin links with regular-file executable forwarders."""
    plugin = Path(os.path.abspath(plugin))
    check_local_path(plugin)
    if plugin.is_symlink():
        raise ValueError("Plugin root must not be a symlink")
    if not plugin.is_dir():
        raise ValueError("Plugin directory does not exist")
    links = []
    for directory, dirs, files in os.walk(plugin, followlinks=False):
        for name in sorted(dirs + files):
            entry = Path(directory) / name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode):
                if entry.parent.name != ".bin" or entry.parent.parent.name != "node_modules":
                    raise ValueError("Unexpected link outside an npm bin directory: " + str(entry.relative_to(plugin)))
                target = local_target(entry, plugin)
                if not target.is_file() or not os.access(target, os.X_OK):
                    raise ValueError("npm target must be an executable file: " + str(entry.relative_to(plugin)))
                links.append({"path": str(entry.relative_to(plugin)), "target": os.readlink(entry),
                              "forward_target": os.path.relpath(target, entry.parent)})
            elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError("Unsupported plugin entry: " + str(entry.relative_to(plugin)))
    changes = ["Forward npm command: " + record["path"] for record in links]
    if not apply or not links:
        return changes
    save_backup(backup, "context-mode-links", {"plugin": str(plugin), "links": links})
    for record in links:
        entry = plugin / record["path"]
        if not entry.is_symlink() or os.readlink(entry) != record["target"]:
            raise ValueError("Plugin changed during repair; stop and review the backup")
        local_target(entry, plugin)
        wrapper = '#!/bin/sh\nexec "$(dirname -- "$0")"/' + shlex.quote(record["forward_target"]) + ' "$@"\n'
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=entry.parent,
                                             prefix=".agent-forwarder-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(wrapper)
                stream.flush()
                os.fchmod(stream.fileno(), 0o755)
            os.replace(temporary, entry)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return changes


def link_destination(path: Path) -> Path:
    return Path(os.path.normpath(str(path.parent / os.readlink(path))))


def latest_plugin(home: Path, relative: str) -> Path:
    base = home / ".codex/plugins/cache" / relative
    check_local_path(base)
    if not base.is_dir():
        return None
    candidates = [p for p in base.iterdir() if not p.is_symlink() and p.is_dir()
                  and all(part.isdigit() for part in p.name.split("."))]
    if not candidates:
        return None
    return max(candidates, key=lambda p: tuple(int(n) for n in p.name.split(".")))


def install_shared_skills(agent_home: Path, repository: Path, apply: bool = False) -> List[str]:
    """Consolidate personal skills; all conflicts are detected before mutations."""
    home, repository = Path(os.path.abspath(agent_home)), Path(os.path.abspath(repository))
    reject_cloud(home)
    reject_cloud(repository)
    shared = home / ".agents/skills"
    helper = repository / ".agents/skills/mac-helper"
    instruction_source = helper / "references/shared-instructions.md"
    if not (helper / "SKILL.md").is_file() or not instruction_source.is_file():
        raise ValueError("Portable helper skill is missing from this repository")
    for root in [home / name for name in (".agents", ".codex", ".claude", ".gemini")]:
        check_local_path(root)
        if root.is_symlink():
            raise ValueError("Unexpected agent root symlink: " + str(root))
    if shared.is_symlink():
        raise ValueError("Canonical shared skills directory must not be a symlink")
    check_local_path(shared)
    operations = []
    planned = set()
    for agent in (".codex", ".claude", ".gemini"):
        source = home / agent / "skills"
        if source.is_symlink():
            if link_destination(source) != shared:
                raise ValueError("Unexpected skill root symlink outside the shared library: " + str(source))
            continue
        if not source.exists():
            operations.append(("link", shared, source))
            continue
        if not source.is_dir():
            raise ValueError("Skill root must be a directory: " + str(source))
        for entry in sorted(source.iterdir()):
            if entry.name.startswith("."):
                continue
            destination = shared / entry.name
            if entry.is_symlink() and link_destination(entry) == destination:
                continue
            if entry.is_symlink():
                raise ValueError("Unexpected personal skill symlink: " + str(entry))
            if not entry.is_dir():
                continue
            if destination.exists() or destination.is_symlink() or destination in planned:
                raise ValueError("Shared skill name conflict: " + entry.name)
            planned.add(destination)
            operations.append(("move", entry, destination))
            if agent == ".codex":
                operations.append(("link", destination, entry))
        if agent != ".codex":
            operations.extend((("retire-root", source, source), ("link", shared, source)))

    desired_links = [(helper, shared / "mac-helper")]
    for relative, name in (("context-mode/context-mode", "context-mode"),
                           ("openai-curated-remote/superpowers", "superpowers")):
        plugin = latest_plugin(home, relative)
        if plugin is not None:
            check_local_path(plugin / "skills")
        if plugin is not None and (plugin / "skills").is_dir():
            desired_links.append((plugin / "skills", shared / name))
    for target, destination in desired_links:
        if destination in planned:
            raise ValueError("Shared skill name conflict: " + destination.name)
        if destination.is_symlink():
            if link_destination(destination) == target:
                continue
            if destination.name not in ("superpowers", "context-mode", "mac-helper"):
                raise ValueError("Shared skill link conflict: " + destination.name)
        elif destination.exists():
            raise ValueError("Shared skill name conflict: " + destination.name)
        operations.append(("link", target, destination))

    common_instructions = home / ".agents/AGENTS.md"
    if common_instructions.is_symlink() and link_destination(common_instructions) != instruction_source:
        raise ValueError("Shared instructions have an unexpected symlink")
    if not common_instructions.exists() and not common_instructions.is_symlink():
        operations.append(("link", instruction_source, common_instructions))
    elif not common_instructions.is_symlink():
        raise ValueError("Existing shared instructions conflict; preserve and reconcile them first")
    marker = "<!-- shared-mac-helper -->"
    for relative in (".codex/AGENTS.md", ".claude/CLAUDE.md", ".gemini/GEMINI.md"):
        destination = home / relative
        if destination.is_symlink():
            if link_destination(destination) != common_instructions:
                raise ValueError("Unexpected instructions symlink: " + str(destination))
            continue
        if destination.exists():
            if marker not in destination.read_text(encoding="utf-8"):
                operations.append(("append", common_instructions, destination))
        else:
            operations.append(("link", common_instructions, destination))
    changes = [kind + ": " + str(destination) for kind, source, destination in operations]
    if not apply or not operations:
        return changes
    records = [{"operation": kind, "source": str(source), "destination": str(destination),
                "previous_link": os.readlink(destination) if destination.is_symlink() else None}
               for kind, source, destination in operations]
    backup_file = save_backup(home / ".agents/backups", "shared-skills", {"operations": records})
    original_files = backup_file.with_suffix("")
    for kind, source, destination in operations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if kind == "move":
            source.rename(destination)
        elif kind == "retire-root":
            original_files.mkdir(exist_ok=True, mode=0o700)
            source.rename(original_files / (source.parent.name + "-skills"))
        elif kind == "link":
            if destination.is_symlink():
                destination.unlink()
            destination.symlink_to(source, target_is_directory=source.is_dir())
        elif kind == "append":
            original_files.mkdir(exist_ok=True, mode=0o700)
            saved = original_files / (destination.parent.name + "-" + destination.name)
            shutil.copy2(destination, saved)
            saved.chmod(0o600)
            with destination.open("a", encoding="utf-8") as stream:
                stream.write("\n\n" + marker + "\nRead and follow the shared local agent guidance at "
                             + str(source) + ". Use its canonical personal skill library.\n")
    return changes


def write_inventory(report: Path, inventory: dict) -> None:
    check_local_path(report)
    report.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=report.parent,
                                         prefix=".mac-helper-", delete=False) as stream:
            temporary = Path(stream.name)
            os.fchmod(stream.fileno(), 0o600)
            json.dump(inventory, stream, indent=2)
            stream.write("\n")
        os.replace(temporary, report)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def machine_inventory(repository: Path) -> dict:
    """Collect only non-identifying, task-relevant OS and agent observations."""
    def command(args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=6)
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None
    tools = {}
    for name in ("codex", "claude", "gemini", "cce", "node"):
        executable = shutil.which(name)
        tools[name] = {"executable": executable, "version": command([executable, "--version"]) if executable else None}
    return {"observed_at": datetime.now(timezone.utc).isoformat(),
            "repository": str(repository), "macos": command(["/usr/bin/sw_vers", "-productVersion"]),
            "build": command(["/usr/bin/sw_vers", "-buildVersion"]),
            "architecture": command(["/usr/bin/uname", "-m"]),
            "hardware_model": command(["/usr/sbin/sysctl", "-n", "hw.model"]),
            "memory_bytes": command(["/usr/sbin/sysctl", "-n", "hw.memsize"]), "tools": tools}


class LocalJsonRpc:
    """Bounded local stdio diagnostics; never starts a model turn."""

    def __init__(self, command, cwd, protocol="mcp", timeout=15, env=None):
        self.command, self.cwd, self.protocol = command, cwd, protocol
        self.timeout, self.env = timeout, env
        self.buffer, self.serial, self.notifications = b"", 0, []
        self.process = None
        self.errors = None

    def __enter__(self):
        self.errors = tempfile.TemporaryFile()
        try:
            self.process = subprocess.Popen(self.command, cwd=self.cwd, env=self.env,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.errors, start_new_session=True)
            info = {"name": "local-agent-tooling-check", "version": "1"}
            params = ({"clientInfo": info, "capabilities": {"experimentalApi": True}}
                      if self.protocol == "codex" else
                      {"protocolVersion": "2024-11-05", "clientInfo": info, "capabilities": {}})
            self.request("initialize", params)
            self.send({"method": "initialized" if self.protocol == "codex" else "notifications/initialized", "params": {}})
            return self
        except BaseException:
            self.close()
            raise

    def send(self, message):
        self.process.stdin.write((json.dumps({"jsonrpc": "2.0", **message}) + "\n").encode())
        self.process.stdin.flush()

    def next_message(self, deadline):
        while True:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                if line.strip():
                    message = json.loads(line)
                    if not isinstance(message, dict):
                        raise ValueError("Invalid local JSON-RPC message")
                    return message
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Local JSON-RPC diagnostic timed out")
            if select.select([self.process.stdout], [], [], min(remaining, 0.5))[0]:
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    self.errors.seek(0)
                    detail = self.errors.read(1000).decode(errors="replace").strip()
                    raise ValueError("Local diagnostic process closed: " + detail)
                self.buffer += chunk
                if len(self.buffer) > 2 * 1024 * 1024:
                    raise ValueError("Local diagnostic response exceeded 2 MiB")

    def request(self, method, params):
        self.serial += 1
        request_id = self.serial
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            message = self.next_message(deadline)
            if message.get("id") == request_id:
                if "error" in message:
                    raise ValueError(str(message["error"].get("message", "Local RPC failed"))[:1000])
                return message.get("result")
            if "method" in message:
                self.notifications.append(message)
                self.notifications = self.notifications[-100:]

    def close(self):
        if self.process is not None:
            if self.process.poll() is None:
                try:
                    os.killpg(self.process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(self.process.pid, signal.SIGKILL)
                    self.process.wait()
            for pipe in (self.process.stdin, self.process.stdout):
                if pipe:
                    pipe.close()
        if self.errors:
            self.errors.close()

    def __exit__(self, *args):
        self.close()


def check_agent_tools(repository):
    """Check native hooks and only this repository's local CCE/CTX transports."""
    checks = []

    def result(name, operation):
        try:
            detail = operation()
            checks.append({"name": name, "ok": True, "detail": detail})
        except (OSError, ValueError, TimeoutError, subprocess.SubprocessError) as error:
            checks.append({"name": name, "ok": False, "detail": str(error)[:1000]})

    def run(command):
        completed = subprocess.run(command, cwd=repository, capture_output=True, text=True, timeout=15)
        if completed.returncode:
            raise ValueError((completed.stderr or completed.stdout).strip()[:1000])
        return completed.stdout.strip()

    try:
        reject_cloud(Path(os.path.abspath(repository)))
        repository = Path(run(["git", "rev-parse", "--show-toplevel"]))
        codex = shutil.which("codex")
        if not codex:
            raise ValueError("codex is not on PATH")
        version = run([codex, "--version"])
        servers = json.loads(run([codex, "mcp", "list", "--json"]))
        checks.append({"name": "Codex CLI", "ok": True, "detail": version})
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return [{"name": "Codex configuration", "ok": False, "detail": str(error)[:1000]}]

    def hooks():
        with LocalJsonRpc([codex, "app-server", "--stdio", "--strict-config"], repository, protocol="codex") as client:
            data = client.request("hooks/list", {"cwds": [str(repository)]})
            skills = client.request("skills/list", {"cwds": [str(repository)]})
        rows = data.get("data", [])
        if any(row.get("errors") for row in rows):
            raise ValueError("Native hook discovery reports errors")
        found = [hook for row in rows for hook in row.get("hooks", [])
                 if "context-mode" in hook.get("command", "") or "context-mode" in (hook.get("pluginId") or "")]
        expected = {"pretooluse", "posttooluse", "sessionstart", "precompact", "userpromptsubmit", "stop"}
        actual = {re.sub("[^a-z]", "", hook["eventName"].lower()) for hook in found}
        if len(found) != 6 or actual != expected or any(
                not h.get("enabled") or h.get("trustStatus") not in ("trusted", "managed")
                or h.get("source") != "user" for h in found):
            raise ValueError("Expected six enabled, trusted native user CTX hooks; check Codex /hooks")
        required = {"context-mode", "ctx-doctor", "ctx-index", "ctx-insight", "ctx-purge", "ctx-search", "ctx-stats", "ctx-upgrade"}
        available = {skill.get("name", "").split(":")[-1]
                     for row in skills.get("data", []) for skill in row.get("skills", [])}
        if not required.issubset(available):
            raise ValueError("Required CTX skills missing: " + ", ".join(sorted(required - available)))
        return "6 enabled/trusted global hooks and 8 CTX skills; no packaging errors"

    def local_server(name):
        for server in servers:
            transport = server.get("transport", {})
            args = transport.get("args") or []
            matches = server.get("name") == "context-mode" if name == "CTX" else any(
                argument == "--project-dir" and i + 1 < len(args)
                and os.path.abspath(args[i + 1]) == str(repository) for i, argument in enumerate(args))
            if not server.get("enabled", True) or not matches:
                continue
            if transport.get("type") != "stdio" or not transport.get("command"):
                raise ValueError(name + " must use local stdio")
            executable = Path(transport["command"]).name
            native_cce = name == "CCE" and executable == "cce" and args[:1] == ["serve"]
            native_ctx = name == "CTX" and (
                (executable == "context-mode" and not args)
                or (executable in ("node", "bun") and len(args) == 1
                    and Path(args[0]).name in ("context-mode", "cli.bundle.mjs", "server.bundle.mjs")))
            if not (native_cce or native_ctx) or any("://" in arg for arg in args):
                raise ValueError(name + " must launch the installed local tool; remote/proxy wrappers are not probed")
            if transport.get("cwd") is not None and os.path.abspath(transport["cwd"]) != str(repository):
                raise ValueError(name + " is pinned to another repository")
            env = os.environ.copy()
            env.update(transport.get("env") or {})
            if name == "CCE":
                env.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1")
            return [transport["command"], *args], env
        raise ValueError("No matching local " + name + " registration for " + str(repository))

    def tool(client, name, arguments):
        data = client.request("tools/call", {"name": name, "arguments": arguments})
        if not isinstance(data, dict):
            raise ValueError(name + " failed")
        text = "\n".join(item.get("text", "") for item in data.get("content", []) if item.get("type") == "text")
        if data.get("isError"):
            raise ValueError(name + ": " + text[:500])
        return text

    def cce():
        command, env = local_server("CCE")
        with LocalJsonRpc(command, repository, env=env) as client:
            status = tool(client, "index_status", {})
            if not re.search(r"\bIndex status:\s*operational\b", status, re.IGNORECASE):
                raise ValueError("CCE index is not operational: " + status[:300])
            tool(client, "context_search", {"query": "local agent setup", "top_k": 1, "max_tokens": 200})
        return "exact-root local index and search respond: " + str(repository)

    def ctx():
        command, env = local_server("CTX")
        with LocalJsonRpc(command, repository, env=env) as client:
            output = tool(client, "ctx_execute", {"language": "javascript", "code": "console.log(6 * 7)"})
            if not re.search(r"^42\s*$", output, re.MULTILINE):
                raise ValueError("CTX did not produce the expected execution result")
            try:
                tool(client, "ctx_search", {"queries": ["tooling diagnostics"], "limit": 1})
            except ValueError as error:
                if re.search(r"(?:^ctx_search:\s*|\n)Knowledge base is empty\b", str(error)):
                    return "local execution verified; search responds (knowledge base empty)"
                raise
        return "local execution and persistent search respond"

    result("Native CTX hooks", hooks)
    result("Local CCE", cce)
    result("Local CTX", ctx)
    return checks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-context-mode", metavar="PLUGIN", type=Path,
                        help="repair only internal npm command links in this plugin")
    parser.add_argument("--share-skills", action="store_true", help="consolidate personal skills into ~/.agents/skills")
    parser.add_argument("--agent-home", type=Path, default=Path.home(), help="agent home (default: current user's home)")
    parser.add_argument("--inventory", action="store_true", help="print sanitized Mac observations; --yes also saves ignored local JSON")
    parser.add_argument("--check-tools", action="store_true", help="check native hooks and current-repository local CCE/CTX; no configuration changes")
    parser.add_argument("--backup-dir", type=Path, default=TOOLING / "logs/agent-setup-backups")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--yes", action="store_true", help="apply the selected backed-up changes")
    args = parser.parse_args(argv)
    if args.check_tools:
        if args.repair_context_mode or args.share_skills or args.inventory:
            parser.error("--check-tools cannot be combined with setup changes")
        checks = check_agent_tools(Path.cwd())
        for check in checks:
            print(("PASS" if check["ok"] else "FAIL") + "  " + check["name"] + ": " + check["detail"])
        return 0 if checks and all(check["ok"] for check in checks) else 1
    if args.repair_context_mode is None and not args.share_skills and not args.inventory:
        parser.error("select --check-tools, --repair-context-mode PLUGIN, --share-skills, or --inventory")
    try:
        changes = []
        if args.repair_context_mode is not None:
            changes.extend(repair_plugin(args.repair_context_mode, args.backup_dir, args.yes))
        if args.share_skills:
            changes.extend(install_shared_skills(args.agent_home, REPOSITORY, args.yes))
        if args.inventory:
            inventory = machine_inventory(REPOSITORY)
            print(json.dumps(inventory, indent=2))
            if args.yes:
                report = TOOLING / "config/mac-helper.local.json"
                write_inventory(report, inventory)
    except (OSError, ValueError) as error:
        print("Agent setup: " + str(error), file=sys.stderr)
        return 1
    print(("Applied" if args.yes else "Preview") + ": " + str(len(changes)) + " changes")
    for change in changes[:16]:
        print("  " + change)
    if len(changes) > 16:
        print("  Additional changes: " + str(len(changes) - 16))
    if args.yes and changes and args.repair_context_mode is not None:
        print("Backup: " + str(args.backup_dir))
        print("Reapprove the repaired plugin hooks in Codex before testing a new session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
