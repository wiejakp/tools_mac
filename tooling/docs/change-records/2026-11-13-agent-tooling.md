# Global agent tooling reliability — 2026-11-13

## Request, evidence and scope

The user requests working agent tooling and reports repeated context-mode plugin
packaging failures for node_modules/.bin/esbuild. lstat confirms that entry is a
symlink again; preview identifies 14 internal npm bin symlinks. Earlier forwarder
repair did not hold. The installed 1.0.169 plugin includes dependency bootstrap
code that can run npm install. Codex rejects symlinks before invoking plugin hooks.
The exact trigger that restored these links has not been established.

Official OpenAI documentation supports global native hooks in ~/.codex/hooks.json
independently of plugins. The installed local context-mode CLI supports its hook
dispatcher and ships all six Codex hook modules. Its MCP and canonical personal
skills already exist independently of the cached plugin registration.

Use those native hooks rather than repeatedly rewriting npm-managed package
contents. Preserve all six events and matchers, with a 20-second command timeout. Retire only the broken duplicate
plugin registration after preparing the replacement. Pin existing local Node/CTX
executables and prepend their runtime PATH for GUI/CLI consistency; keep CTX cwd
dynamic and preserve routine tool approvals. Do not install packages, upgrade,
disable lifecycle hooks, bypass trust, invent trust hashes, touch auth files,
reindex another project or launch another model/provider.

## Exact affected files/settings/processes

Global: /Users/pwiejak/.codex/config.toml and the originally absent
/Users/pwiejak/.codex/hooks.json. Only context-mode plugin selection, its stdio
command/args/environment, six native hook trust states and the documented
project_doc_max_bytes limit change. Other MCPs,
projects, credentials and user settings stay outside the change.

Project: src/local_scripts/agent_setup.py, tests/test_agent_setup.py, Makefile,
README.md, AGENTS.md and the deterministic PTY fixture in tests/test_sites_cleaner.py;
new docs/agent-clients.md, this change record and
docs/superpowers/plans/2026-11-13-agent-tooling.md. Preserve the earlier cache-cleaner
implementation and test changes. Existing native make codex/agent/gemini recipes stay.

Recovery/candidates/evidence: ignored logs/change-backups/2026-11-13-agent-tooling/,
mode 0700; JSON mode 0600. project.before.json and global.before.json capture
original bytes, modes and absent paths before mutation. Two prepared candidate
files hold six native hook definitions and precise native config edits.

Owned diagnostics: bounded local stdio app-server/proxy, local CCE and CTX
processes; ephemeral native thread without a model turn only when needed to prove
hook execution. Stop only owned processes/connections. No conversation prompt or
repository content goes to another provider. Codex/CTX may update their own local
session statistics; no private data is sent to third-party services.

## Ordered plan and verification

1. Capture originals; prepare exact hook definitions and config edits locally.
2. Add regression-tested bounded local JSON-RPC/health checks to the existing
   agent-setup helper and a make check-agent-tools target; no new launcher/daemon.
3. Audit replacement commands; atomically install only the new global hooks file.
4. Use native Codex config APIs to retire the broken plugin registration, pin the
   existing CTX runtime and trust only the six hashes returned by native hooks/list.
   Preserve unrelated hook states. Use version/hash guards against later edits.
5. Verify six enabled/trusted native hooks and attempt native SessionStart execution,
   local CTX execution/search, exact-root CCE status/retrieval and native skill
   discovery. Keep native trust, execution, MCP and index evidence separate.
6. Run focused regressions, make verify and diff checks; document CLI/GUI scope,
   lifecycle expectations, remaining limitations and the repeatable health command.
7. Save final bytes/modes/hash descriptors and guarded rollback; refresh only changed
   source/test CCE paths. Retain prior task recovery archives unchanged.

## Rollback, defined before implementation

1. Stop edits to the affected files. Use this task's project/global before and
   after descriptors; verify archive checksums and current modes/hashes for every
   affected path before any restoration. Refuse later edits or symlinked parents.
2. Atomically restore the exact original global config bytes/mode. Remove only
   the new hooks.json if it still matches this task's final state. Refresh native
   runtime config, or restart only the user's chosen Codex session normally.
   This intentionally restores the original broken plugin selection.
3. Restore existing project files byte-for-byte and modes from project.before.json;
   remove only docs originally absent. Keep prior cache-cleaner edits and all
   unrelated files. Retain recovery archives. No package/npm changes need undoing.
4. Run make verify and git --no-pager diff --check; refresh only restored source/test
   CCE paths. A guarded executable command and tested refusal fixtures will be
   recorded before completion.

Status: implemented and verified within the limits recorded below. Global
configuration, native hooks and the canonical CTX skill directory have changed;
the guarded command below restores their captured originals.


## Additional verified findings before the final configuration edit

- The CLI is 0.165.0 and the already-running managed daemon is 0.169.0. Both
  native runtimes recognize the same six replacement hook trust hashes.
- Proxy attempts against the exact native-reported local control socket timed out
  for both binaries. No daemon or unrelated session was restarted. Fresh runtime
  verification works; existing sessions may need one normal reopen to reload.
- Metadata-only ephemeral startup/shell probes emitted no hook lifecycle run
  notifications. Do not represent those probes as native lifecycle execution.
  Separately, all six real hook handlers exited 0 in disposable local state;
  PreToolUse redirected a simulated curl request without executing any fetch.
- CTX JavaScript execution succeeds. ctx_search reports an empty manual knowledge
  base; this is expected before indexing content, and the checker reports it
  explicitly without adding artificial knowledge or hiding other errors.
- Native startup reported 35,816 combined instruction bytes above the default
  32,768 project_doc_max_bytes limit. Raise that exact global setting to 65,536
  so current project/privacy instructions are not subject to that limit warning.
  This additional leaf setting is covered by the original config backup and
  guarded rollback; no agent instruction text is weakened or removed.

## Canonical skill dependency, recorded before migration

The exact `/Users/pwiejak/.agents/skills/context-mode` path is a symlink to
`/Users/pwiejak/.codex/plugins/cache/context-mode/context-mode/1.0.169/skills`.
Retiring the plugin while retaining that link would leave skill availability
dependent on an old cache version. Replace only this link with physical copies
of its existing skill bytes and modes. Preserve the original link in this task's
private recovery directory, snapshot every source file/mode before copying, and
verify the resulting tree. No source package files or other personal skills move.

Rollback must first validate every copied file, mode and directory entry plus
the saved original link. Refuse later edits or unexpected entries before any
mutation. Remove only the validated copies and empty directories, then rename
the original saved link back to its exact location. Retain before snapshots.

## Durable local audit knowledge

Record a dated repository decision and code-area note in this exact repository's
local CCE, then recall them to verify persistence. These are historical audit
records, retained like the private recovery archive. If the implementation is
rolled back, append a dated reversal using the same local `record_decision` tool
so future recall does not treat the migration as current. No temporary raw logs,
credentials or private payloads are stored. Functional code/config/skill rollback
remains byte/mode guarded; ordinary diagnostics/statistics and audit history are
not purged as part of rollback.

## Exact guarded rollback command

Run from normal Terminal, after stopping edits to the affected files. This checks
all project/global/skill scopes before restoring any existing file. It intentionally
restores the previous broken plugin configuration and preserves audit history.

```sh
python3 -B - <<'ROLLBACK'
import os, pathlib, json, stat, hashlib, base64, uuid, subprocess

FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def open_dir(path):
    path = pathlib.Path(os.path.abspath(path))
    blocked = ("cloudstorage", "mobile documents", "googledrive", "google drive",
               "onedrive", "sharepoint", "dropbox", "icloud", "fileprovider", "file provider")
    require(not any(word in str(path).lower() for word in blocked)
            and not any(part.lower() == "box" for part in path.parts), "Cloud path refused")
    fd = os.open(path.anchor, FLAGS)
    try:
        for part in path.parts[1:]:
            child = os.open(part, FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise

def file_signature(parent, name, expected):
    info = os.stat(name, dir_fd=parent, follow_symlinks=False)
    require(stat.S_ISREG(info.st_mode), "Changed file type: " + name)
    require(info.st_size == expected["size"], "Later file edit: " + name)
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
    with os.fdopen(fd, "rb") as stream:
        actual = os.fstat(stream.fileno())
        require((actual.st_dev, actual.st_ino) == (info.st_dev, info.st_ino), "File changed during validation")
        data = stream.read(expected["size"] + 1)
    return {"kind": "file", "size": len(data), "mode": stat.S_IMODE(actual.st_mode),
            "sha256": hashlib.sha256(data).hexdigest()}

def check_tree(fd, expected, relative="."):
    saved = expected[relative]
    names = sorted(os.listdir(fd))
    require(names == saved["entries"], "Later skill entries: " + relative)
    require(stat.S_IMODE(os.fstat(fd).st_mode) == saved["mode"], "Skill directory mode changed")
    for name in names:
        key = (pathlib.Path(relative) / name).as_posix()
        item = expected[key]
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if item["kind"] == "directory":
            require(stat.S_ISDIR(info.st_mode), "Changed skill directory")
            child = os.open(name, FLAGS, dir_fd=fd)
            try:
                require((os.fstat(child).st_dev, os.fstat(child).st_ino) == (info.st_dev, info.st_ino), "Skill directory changed")
                check_tree(child, expected, key)
            finally:
                os.close(child)
        else:
            wanted = {"kind": "file", "size": len(base64.b64decode(item["content_base64"])),
                      "mode": item["mode"], "sha256": item["sha256"]}
            require(file_signature(fd, name, wanted) == wanted, "Later skill file edit: " + key)

def erase_owned_tree(fd, expected, relative="."):
    for name in expected[relative]["entries"]:
        key = (pathlib.Path(relative) / name).as_posix()
        if expected[key]["kind"] == "directory":
            child = os.open(name, FLAGS, dir_fd=fd)
            try:
                erase_owned_tree(child, expected, key)
            finally:
                os.close(child)
            os.rmdir(name, dir_fd=fd)
        else:
            os.unlink(name, dir_fd=fd)

def restore_tooling(project, before_project, before_global, completed, skills_before, skills_after):
    opened, staged, files = [], [], []
    skill_fd = skill_parent = source_fd = original_parent = None
    try:
        require(before_project["repository"] == str(project), "Wrong project identity")
        require(set(before_project["files"]) == set(completed["project_files"]), "Project path set changed")
        require(set(before_global["files"]) == set(completed["global_files"]), "Global path set changed")
        for originals, finals, base in [(before_project["files"], completed["project_files"], project),
                                        (before_global["files"], completed["global_files"], None)]:
            for name, saved in originals.items():
                relative = pathlib.Path(name)
                if base is not None:
                    require(not relative.is_absolute() and ".." not in relative.parts, "Escaping project path")
                path = base / relative if base is not None else relative
                parent = open_dir(path.parent)
                opened.append(parent)
                wanted = {key: finals[name][key] for key in ("kind", "size", "mode", "sha256")}
                require(file_signature(parent, path.name, wanted) == wanted, "Later edit: " + str(path))
                require(os.access(path.parent, os.W_OK | os.X_OK), "Parent is not writable: " + str(path.parent))
                if saved["kind"] == "file":
                    data = base64.b64decode(saved["content_base64"], validate=True)
                    require(hashlib.sha256(data).hexdigest() == saved["sha256"], "Damaged original snapshot")
                else:
                    require(saved["kind"] == "absent", "Unsupported original entry")
                files.append((parent, path.name, saved, wanted))
        skill = pathlib.Path(skills_before["path"])
        require(skills_after["path"] == str(skill), "Skill destination changed")
        skill_parent = open_dir(skill.parent)
        skill_fd = os.open(skill.name, FLAGS, dir_fd=skill_parent)
        check_tree(skill_fd, skills_after["tree"])
        source_fd = open_dir(skills_before["source"])
        check_tree(source_fd, skills_before["tree"])
        original = pathlib.Path(skills_before["saved_link"])
        original_parent = open_dir(original.parent)
        link_info = os.stat(original.name, dir_fd=original_parent, follow_symlinks=False)
        require(stat.S_ISLNK(link_info.st_mode)
                and os.readlink(original.name, dir_fd=original_parent) == skills_before["original"]["target"]
                and stat.S_IMODE(link_info.st_mode) == skills_before["original"]["mode"], "Original skill link changed")
        require(os.fstat(skill_parent).st_dev == os.fstat(original_parent).st_dev, "Recovery link moved to another filesystem")
        require(os.access(skill.parent, os.W_OK | os.X_OK), "Skill parent is not writable")
        # Every scope has passed validation before any existing file is changed.
        for parent, name, saved, wanted in files:
            if saved["kind"] == "file":
                temporary = ".agent-tooling-undo-" + uuid.uuid4().hex
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
                staged.append((parent, temporary, name))
                with os.fdopen(fd, "wb") as stream:
                    os.fchmod(stream.fileno(), saved["mode"])
                    stream.write(base64.b64decode(saved["content_base64"]))
                    stream.flush()
                    os.fsync(stream.fileno())
        for parent, name, saved, wanted in files:
            require(file_signature(parent, name, wanted) == wanted, "File changed while staging rollback")
        check_tree(skill_fd, skills_after["tree"])
        for parent, temporary, name in staged:
            os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
        for parent, name, saved, wanted in files:
            if saved["kind"] == "absent":
                os.unlink(name, dir_fd=parent)
        erase_owned_tree(skill_fd, skills_after["tree"])
        current = os.stat(skill.name, dir_fd=skill_parent, follow_symlinks=False)
        require((current.st_dev, current.st_ino) == (os.fstat(skill_fd).st_dev, os.fstat(skill_fd).st_ino), "Skill root changed")
        os.rmdir(skill.name, dir_fd=skill_parent)
        os.rename(original.name, skill.name, src_dir_fd=original_parent, dst_dir_fd=skill_parent)
        require(os.readlink(skill.name, dir_fd=skill_parent) == skills_before["original"]["target"], "Skill link restoration failed")
        for parent, name, saved, wanted in files:
            if saved["kind"] == "absent":
                try:
                    os.stat(name, dir_fd=parent, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise RuntimeError("New file not removed: " + name)
            original_data = base64.b64decode(saved["content_base64"])
            expected = {"kind": "file", "size": len(original_data), "mode": saved["mode"], "sha256": saved["sha256"]}
            require(file_signature(parent, name, expected) == expected, "Original file verification failed")
    finally:
        for parent, temporary, _ in staged:
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
        for fd in [skill_fd, skill_parent, source_fd, original_parent, *opened]:
            if fd is not None:
                os.close(fd)

if __name__ == "__main__":
    root = pathlib.Path("/Users/pwiejak/Desktop/tools")
    require(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=root, text=True).strip() == str(root), "Wrong Git root")
    backup = root / "logs/change-backups/2026-11-13-agent-tooling"
    fd = open_dir(backup)
    os.close(fd)
    after = json.loads((backup / "after.json").read_text())
    checksum = after.pop("payload_sha256")
    require(hashlib.sha256(json.dumps(after, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == checksum, "Recovery manifest changed")
    originals = {}
    for name, digest in after["archives"].items():
        data = (backup / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == digest, "Recovery archive changed: " + name)
        originals[name] = json.loads(data)
    expected_project = {"src/local_scripts/agent_setup.py", "tests/test_agent_setup.py", "Makefile", "README.md",
                        "AGENTS.md", "tests/test_sites_cleaner.py", "docs/agent-clients.md", "docs/change-records/2026-11-13-agent-tooling.md",
                        "docs/superpowers/plans/2026-11-13-agent-tooling.md"}
    require(set(after["project_files"]) == expected_project, "Unexpected project recovery paths")
    require(set(after["global_files"]) == {"/Users/pwiejak/.codex/config.toml", "/Users/pwiejak/.codex/hooks.json"}, "Unexpected global paths")
    skill = originals["context-skills.before.json"]
    require(skill["path"] == "/Users/pwiejak/.agents/skills/context-mode"
            and skill["source"] == "/Users/pwiejak/.codex/plugins/cache/context-mode/context-mode/1.0.169/skills"
            and skill["saved_link"] == str(backup / "context-mode.original-link"), "Unexpected skill recovery paths")
    restore_tooling(root, originals["project.before.json"], originals["global.before.json"], after,
                    skill, originals["context-skills.after.json"])
    print("Original project/global bytes and modes restored; only this task's new docs/hooks/skill copies removed.")
    print("Original canonical skill link restored. Keep the audit/recovery archive and record a dated CCE reversal.")
ROLLBACK
```

After restoration:

```sh
make verify
git --no-pager diff --check
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 cce index --path /Users/pwiejak/Desktop/tools/src/local_scripts/agent_setup.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 cce index --path /Users/pwiejak/Desktop/tools/tests/test_agent_setup.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 cce index --path /Users/pwiejak/Desktop/tools/tests/test_sites_cleaner.py
```

Reopen only the affected Codex session to load restored settings. In this exact
repository's local CCE, append `record_decision(decision="Rolled back the 2026-11-13
agent tooling migration; its earlier notes are historical.", reason="Restored the
captured original config, project files and canonical skill link.")`. Keep the
private recovery archive; do not purge indexes, delete unrelated notes or restart
unrelated Codex sessions.

## Verification fixture correction, captured before editing

The final 104-test run exposed an existing nondeterministic PTY test in
`tests/test_sites_cleaner.py`: it requires the literal label Space saved after
removing a nine-byte fixture, but real shared-volume free space decreased by
116 KiB during that run, correctly producing Free space change. This test checks
terminal lifetime, not disk accounting; dedicated tests already cover signed
disk changes. Pin its child process's disk measurements to deterministic fixture
values. Do not alter cleaner behavior or weaken the output/lifetime assertions.

The exact current bytes/mode (including the earlier cache task's changes) were
added to project.before.json before this correction. The initial archive and
failed test output are retained separately. Add this ninth project path to the
guarded rollback allowlist and refresh only this additional test path in CCE.

## Final results and practical limits

- `make verify` passed: 104 tests in 8.687 seconds, plus the repository's syntax
  checks. The earlier shared-volume PTY failure and its deterministic correction
  are retained in the recovery evidence; production cleaner behavior was unchanged
  by this tooling task.
- `make check-agent-tools` exited 0: native Codex CLI responds, six global CTX
  hooks are enabled and trusted, eight CTX skills are discoverable, exact-root
  local CCE status/search work, and actual local CTX execution/search work.
  Empty manual CTX knowledge bases are reported explicitly; other errors fail.
- Native CLI 0.165.0 and managed runtime 0.169.0 recognize the same six hook
  hashes without the cached-plugin packaging failure. All six real CTX handler
  commands separately exited 0 with synthetic inputs and disposable local state.
  No model turn or remote fetch was started to test them.
- Metadata-only native startup/shell probes produced no lifecycle run events.
  End-to-end native lifecycle execution during a new model turn remains
  unobserved. The running daemon's proxy reload timed out; no unrelated session
  or daemon was restarted. Reopen an affected existing session once if it still
  displays the old cached-plugin error. New runtime discovery uses native hooks.
- All 13 copied skill files match captured source bytes and modes; the original
  link is preserved for rollback. The cached npm package was not modified.
- Seven disposable rollback cases passed: original restoration, and refusal of
  later project/global/skill edits, an extra skill entry, a symlink and a mode
  change. Refusal occurs before changing existing files.
- Only the three changed helper/test paths were refreshed in CCE; all exited 0.
  A dated local decision/code-area note was written and successfully recalled.
  No full reindex, package installation, scheduled job, real-app cleanup or
  third-party analysis was performed. Native client launch recipes are unchanged.
- Final bytes, modes and archive checksums are in the private `after.json`;
  `verification.json` retains full test/health output and tested source hashes.
  Diagnostics stop only their own bounded child processes. Health checks report
  current status; they cannot guarantee that future package updates never fail.
