# Local disk-space scan — 2026-11-13

## Request, scope and ordered actions

The user requested a system disk-space scan and an explanation of what uses it.
This task authorizes read-only local disk usage diagnostics. It replaces active
implementation work for the duration of this request; preserve that earlier work.

1. Read native volume capacity and local snapshot metadata.
2. Measure allocated bytes in selected local application, developer, user-data
   and temporary directories. Do not scan a home/root tree indiscriminately.
3. Exclude cloud storage, File Provider locations, credentials, symlinks and
   external/network volumes before descent. Read metadata only, never file bodies.
4. Inspect the largest measured local subdirectories and files. Report allocated
   sizes, sparse-file logical sizes separately, denied paths and scan limitations.
5. Save a private local summary and return the main results directly in chat.

## Exact effects and risks

No cleanup, package installation, settings changes, mounts, daemon restart or
network calls. Diagnostic subprocesses are owned, bounded and stopped on finish.
Permission-denied paths stay excluded; do not retry protected user-data paths.
Disk sizes can change during the scan. Hard links and APFS clones/snapshots may
make directory attribution differ from whole-volume usage; report that limit.

Only these new artifacts are written:
- `docs/change-records/2026-11-13-disk-space-scan.md` (this audit record)
- `logs/change-backups/2026-11-13-disk-space-scan/before.json`
- `logs/change-backups/2026-11-13-disk-space-scan/after.json`
- `logs/disk-space-2026-11-13.json` (private, ignored metadata summary)

Every artifact and the task-specific backup directory were absent before work.
No existing project, system or user file is modified.

## Verification and rollback

Verify native command exit codes, volume/device boundaries, excluded-path guards,
complete traversal of each reported category and correct byte units. Record
permission failures as incomplete measurements. No application test suite is
required for this metadata-only diagnostic.

1. Read `logs/change-backups/2026-11-13-disk-space-scan/after.json` and compare
   every listed artifact's current SHA-256 and mode with the recorded value.
   Refuse removal if any file changed, is a symlink, or a parent is a symlink.
2. Remove only the three recorded new artifact files other than `after.json`,
   using `Path.unlink()`; no system files need restoration.
3. Remove `after.json` last, then use `Path.rmdir()` on the exact empty task
   backup directory. Preserve the existing parent directories and other tasks.
4. Check that the four exact artifact paths and task backup directory are absent.
   The scan caused no other persistent changes and has no cleanup to reverse.

## Results

Completed with bounded/partial measurements. Initial `df -h / /System/Volumes/Data`: data volume 408 GiB used,
1.8 GiB available. `tmutil listlocalsnapshots /` reported no local snapshots.


### Findings and verification

- Scanned metadata for 4,533,573 files in 50 selected categories. The allocated
  total observed was 339.51 GiB; this is not a full-volume accounting.
- `~/sites`: at least 181.16 GiB (time-capped), including `app_hublist` at least
  127.52 GiB, `app_hublist/var/tmp` 96.44 GiB observed and `var/badges` 14.99 GiB.
- `/Applications`: 46.38 GiB observed, including NinjaRMMAgent 12.72 GiB.
- User Application Support: 27.84 GiB, including Cursor 11.12 GiB.
- User Containers: 25.46 GiB, including Docker 22.45 GiB. `Docker.raw` uses
  22.35 GiB of allocated blocks; its 230.97 GiB logical size is sparse.
- User Caches: 20.74 GiB. `~/.cache`: 9.35 GiB, including Codex runtimes 6.90 GiB.
- `~/.codex`: 5.59 GiB. npm cache: 3.28 GiB. Node versions: 2.58 GiB.
- One 12-second native `du -kxP -d 1` follow-up found
  `app_hublist/var/tmp/app-wide-filters-20261013` at 13.38 GiB,
  `sitemap-pinger-final-default-v3` 1.09 GiB and
  `codex-multiple-chats-final` 1.09 GiB. The follow-up was partial and its owned
  process was stopped by `subprocess.run` on timeout.
- The local context-mode call completed and saved the report, although a host
  restart lost the tool handle. Its output file was checked before doing any
  further work; the broad scan was not repeated.
- `diskutil info -plist /System/Volumes/Data` succeeded outside the command
  sandbox; only capacity fields were returned. No protected directory denial
  was retried. `tmutil listlocalsnapshots /` returned no local snapshots.
- System data/settings were unchanged. Free space changed during the scan due
  to other activity; the scan did not delete files. Final live capacity is in
  the report's `latest_volume` object. Earlier client-setup work was preserved.

### Exact guarded rollback command

From `/Users/pwiejak/Desktop/tools`, run the following only to remove this task's
new audit/report artifacts. All validation happens before the first removal.
The manifest includes a canonical payload checksum to reject metadata edits.

```sh
python3 -B - <<'ROLLBACK'
import pathlib, json, hashlib, os, stat, subprocess
root = pathlib.Path('/Users/pwiejak/Desktop/tools')
assert subprocess.check_output(['git','rev-parse','--show-toplevel'], cwd=root, text=True).strip() == str(root)
backup = root / 'logs/change-backups/2026-11-13-disk-space-scan'
manifest = backup / 'after.json'
def no_links(p):
    assert p.is_relative_to(root)
    q = p
    while q != root:
        assert not q.is_symlink(), 'Symlink: ' + str(q)
        q = q.parent
no_links(manifest)
assert stat.S_IMODE(manifest.stat().st_mode) == 0o600
state = json.loads(manifest.read_text())
checksum = state.pop('payload_sha256')
assert hashlib.sha256(json.dumps(state, sort_keys=True, separators=(',',':')).encode()).hexdigest() == checksum, 'Manifest changed'
assert state['repository'] == str(root)
expected = {
    'docs/change-records/2026-11-13-disk-space-scan.md',
    'logs/disk-space-2026-11-13.json',
    'logs/change-backups/2026-11-13-disk-space-scan/before.json',
}
assert set(state['files']) == expected
assert set(x.name for x in backup.iterdir()) == {'before.json', 'after.json'}, 'Unexpected recovery entry'
for name, saved in state['files'].items():
    p = root / name
    no_links(p)
    assert p.is_file() and stat.S_ISREG(p.lstat().st_mode)
    assert hashlib.sha256(p.read_bytes()).hexdigest() == saved['sha256'], 'Later edit: ' + name
    assert stat.S_IMODE(p.stat().st_mode) == saved['mode'], 'Mode changed: ' + name
for name in sorted(expected):
    (root / name).unlink()
manifest.unlink()
backup.rmdir()
assert all(not os.path.lexists(root / name) for name in expected)
assert not os.path.lexists(backup)
print('Removed only the four original-absent diagnostic artifacts; no system changes to restore.')
ROLLBACK
```
