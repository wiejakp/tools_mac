# Site runtime cache/log cleanup — 2026-11-13

## Request, evidence and authorized effects

The user asks why app_hublist occupies at least 127.5 GiB and wants its caches
and logs cleared by the existing cache/log entry points. Earlier metadata showed
96.44 GiB in var/tmp and 14.99 GiB in var/badges. A focused read of the app's
Makefile and scripts/ci/run_phpunit.py confirms that var/badges stores generated
PHPUnit coverage and worker reports. Temporary runs contain additional coverage
reports, HTML coverage and compiled Symfony containers. Existing discovery
explicitly prunes var/tmp and therefore misses these generated outputs.

Only tools-repository code, tests and documentation below change. No real app
file is deleted or modified; no application code is executed. Existing Make,
shell and Finder entry points and their explicit deletion confirmation stay.
No new dependency, service, network request or global configuration change.

Affected paths:
- src/local_scripts/sites_cleaner.py: classify recognized generated runtime
  outputs with metadata-only descriptor traversal; keep deletion descriptor-based.
- tests/test_sites_cleaner.py: disposable deletion-boundary regressions.
- README.md and AGENTS.md: document precise cleanup and preserved data.
- This record and docs/superpowers/plans/2026-11-13-site-runtime-cleanup.md: new.
- Ignored local recovery directory logs/change-backups/2026-11-13-site-runtime-cleanup/.
- After validation, refresh only changed source/test CCE paths; its index is derived
  local data and can be refreshed from restored source during rollback.

## Ordered implementation and verification

1. Preserve bytes, modes and absent paths in the private before.json snapshot.
2. Write regressions and observe missing generated-output cleanup failures.
3. Add bounded classification under recognized apps' var/tmp, var/badges and
   var/coverage; recognize PHPUnit report pairs, HTML coverage structure and
   compiled Symfony container metadata. Do not select the whole temporary tree.
4. Separate CACHE and LOGS; preserve archived app roots, source fixtures, Git,
   dependencies, uploads, databases, sessions, unknown files, links and cloud paths.
5. Refuse replaced generated targets at execution. Preserve protected data dirs
   in generated reports; retain Laravel's legitimate cache/data exception only
   inside its explicit cache root.
6. Run focused regressions, make verify and diff checks. Any real-app check is
   read-only discovery/preview, explicitly bounded, with no cleanup. Test only
   disposable fixtures under tests/ and clean up owned diagnostic processes.
7. Save final descriptors and results. Refresh only changed CCE paths.

## Recovery captured before implementation

before.json stores original bytes/modes of all four existing files and records
both new docs absent. Its SHA-256 is stored in after.json. before/after JSON and
verification results remain ignored and mode 0600; directory mode 0700.

Numbered rollback, using the exact guarded command appended below before completion:
1. Stop editing the six paths; keep the recovery directory. Validate its before
   checksum and every final file hash/mode. Reject later edits or symlinked parents
   before any mutation. Never use git reset, clean, a broad unlink or recursion.
2. Restore the four existing files byte-for-byte and their original modes.
3. Remove only the two docs originally absent. Preserve unrelated user work and
   retain recovery JSON for audit. No real-app deletion needs reversing.
4. Run make verify, git --no-pager diff --check and refresh the restored two CCE
   source/test paths. Global settings and other repositories require no action.

## Decisions and status

Ruling: clean identifiable generated test output as cache, without purging saved
worktrees or all of var/tmp. The request authorizes this extension; no duplicate
scope/plan approval is needed. A missing runtime signature means preserve data.
Coverage reports will need regeneration after the user chooses cache cleanup.
Generic saved reports, source copies and fixtures remain.

Implementation complete; final verification passed. See results below.

## Exact guarded rollback command

From this repository, after stopping edits to the six affected files:

```sh
python3 -B - <<'ROLLBACK'
import os, pathlib, json, hashlib, base64, stat, tempfile, subprocess

def signature(path):
    if path.is_symlink():
        raise RuntimeError("Refusing a symlink: " + str(path))
    try:
        info = path.lstat()
    except FileNotFoundError:
        return {"kind": "absent"}
    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError("Expected a regular file: " + str(path))
    return {"kind": "file", "mode": stat.S_IMODE(info.st_mode),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def restore(root, before, after):
    if before["repository"] != str(root) or after["repository"] != str(root):
        raise RuntimeError("Wrong repository")
    if set(before["files"]) != set(after["files"]):
        raise RuntimeError("Recovery path sets differ")
    staged = []
    try:
        for name, saved in before["files"].items():
            relative = pathlib.Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError("Escaping recovery path")
            path = root / relative
            for parent in [path, *path.parents]:
                if parent == root:
                    break
                if parent.is_symlink():
                    raise RuntimeError("Symlinked recovery path")
            expected = after["files"][name]
            wanted = {k: expected[k] for k in ("kind", "mode", "sha256")}
            if signature(path) != wanted:
                raise RuntimeError("Later edit or mode change: " + name)
            if saved["kind"] == "file":
                content = base64.b64decode(saved["content_base64"], validate=True)
                if hashlib.sha256(content).hexdigest() != saved["sha256"]:
                    raise RuntimeError("Damaged original snapshot: " + name)
            elif saved["kind"] != "absent":
                raise RuntimeError("Unsupported original entry")
        # All later-edit/path checks have passed before the first mutation.
        for name, saved in before["files"].items():
            if saved["kind"] == "file":
                path = root / name
                fd, temporary = tempfile.mkstemp(prefix=".runtime-rollback-", dir=path.parent)
                staged.append((pathlib.Path(temporary), path))
                with os.fdopen(fd, "wb") as stream:
                    os.fchmod(stream.fileno(), saved["mode"])
                    stream.write(base64.b64decode(saved["content_base64"]))
                    stream.flush()
                    os.fsync(stream.fileno())
        for name, expected in after["files"].items():
            if signature(root / name) != {k: expected[k] for k in ("kind", "mode", "sha256")}:
                raise RuntimeError("File changed while staging rollback: " + name)
        for temporary, path in staged:
            os.replace(temporary, path)
        for name, saved in before["files"].items():
            if saved["kind"] == "absent":
                (root / name).unlink()
        for name, saved in before["files"].items():
            wanted = saved if saved["kind"] == "absent" else {k: saved[k] for k in ("kind", "mode", "sha256")}
            if signature(root / name) != wanted:
                raise RuntimeError("Restoration verification failed: " + name)
    finally:
        for temporary, _ in staged:
            if os.path.lexists(temporary):
                temporary.unlink()

if __name__ == "__main__":
    root = pathlib.Path("/Users/pwiejak/Desktop/tools")
    if subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=root, text=True).strip() != str(root):
        raise RuntimeError("Wrong active Git root")
    backup = root / "logs/change-backups/2026-11-13-site-runtime-cleanup"
    for path in [backup, *backup.parents]:
        if path == root:
            break
        if path.is_symlink():
            raise RuntimeError("Symlinked recovery directory")
    for name in ("before.json", "after.json"):
        signature(backup / name)
    original = (backup / "before.json").read_bytes()
    completed = json.loads((backup / "after.json").read_text())
    payload_hash = completed.pop("payload_sha256")
    if hashlib.sha256(json.dumps(completed, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != payload_hash:
        raise RuntimeError("Recovery metadata changed")
    if hashlib.sha256(original).hexdigest() != completed["before_sha256"]:
        raise RuntimeError("Original snapshot checksum mismatch")
    expected = {"src/local_scripts/sites_cleaner.py", "tests/test_sites_cleaner.py",
                "README.md", "AGENTS.md", "docs/change-records/2026-11-13-site-runtime-cleanup.md",
                "docs/superpowers/plans/2026-11-13-site-runtime-cleanup.md"}
    if set(completed["files"]) != expected:
        raise RuntimeError("Unexpected recovery paths")
    restore(root, json.loads(original), completed)
    print("Restored four original files/modes and removed only the two originally absent task docs.")
    print("Keep the recovery archive. Run make verify, then refresh the two restored CCE source/test paths.")
ROLLBACK
```

After rollback, run `make verify`, `git --no-pager diff --check`, then:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 cce index --path /Users/pwiejak/Desktop/tools/src/local_scripts/sites_cleaner.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 cce index --path /Users/pwiejak/Desktop/tools/tests/test_sites_cleaner.py
```

The recovery archive is intentionally retained. No real-app file was changed or
deleted by implementation, so application data needs no restoration.


## Final results and limitations

- Initial regression run demonstrated missing cleanup (five failed assertions
  across six focused tests). New filesystem-boundary, standalone Laravel-cache
  and directory-open race regressions also failed before their corrections.
- Final `make verify`: exit 0, 90 tests in 8.189 seconds; shell/Python syntax
  checks and every disposable deletion/mount/client fixture passed.
- Read-only discovery of app_hublist completed in 18.13 seconds with zero errors.
  It found 2,454 generated CACHE targets, 11,477 LOGS targets and 2,392 directly
  selected coverage/report files accounting for 42.96 GiB of allocated blocks.
  There were 5,706 entries in var/tmp and 124 run directories in var/badges/runs.
  Allocation totals are observations, not guaranteed recovered space; APFS shared
  extents, hard links and changing files affect actual savings.
- The actual app deletion path (`execute_plan`) was never called. This is an
  implementation change for the user's next explicit cache/log cleanup.
- The preview probe preceded the final Laravel/root-directory race corrections;
  those affect execution/boundaries, not the counted app's discovery signatures.
- Existing make/shell/Finder entry points now use the expanded engine. The menu
  names generated test coverage before confirmation. Preview remains non-mutating;
  --yes remains explicit. Existing before/after measured disk summaries remain.
- Generic saved reports, unknown files, screenshots, source fixtures, archived
  applications/worktrees, uploads, data, sessions, dependencies and Git remain.
  Coverage and generated reports need regeneration after cache cleanup.
- Rollback fixture checks passed exact bytes/modes/absent-path restoration and
  refusal of later content edits, mode changes and symlinks before any mutation.
- `git --no-pager diff --check`: exit 0. Only the four declared existing files
  changed; both declared task docs are new. The earlier disk-scan record remains.
- Targeted offline CCE refreshes of the source and test file both exited 0;
  matching CCE MCP index_status reports operational. No full reindex ran.

Full local verification evidence is in ignored
`logs/change-backups/2026-11-13-site-runtime-cleanup/verification.json`.
Original and final bytes/modes and checksums are in before.json and after.json.
The documented rollback command was compiled and exercised on disposable fixtures;
no rollback or cleanup was executed against actual apps or the live working tree.
