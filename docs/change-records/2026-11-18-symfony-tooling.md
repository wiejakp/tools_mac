# Symfony application and portable tooling — 2026-11-18

## Requested outcome and accepted correction

Initialize this checkout with origin `https://github.com/wiejakp/tools_mac.git`,
create a small Symfony application using site-isolated PHP 8.5 at
`https://tools_mac.test`, put the existing personal tools under `tooling/`,
remove machine-specific project-root assumptions, and investigate disk usage.
The user subsequently selected a tools/storage/largest-sites dashboard and
authorized a read-only audit of the whole local Mac. After installed Valet
rejected PHP 8.5, the user explicitly changed the PHP requirement to **8.3**.
The final application therefore uses **Symfony 7.4 LTS / PHP 8.3**, matching the
PHP major/minor in `.valetrc`, `.php-version`, Composer and the command wrapper.
Disk inspection is read-only and excludes cloud storage and mounted shares.

## Initial state and preservation

`git rev-parse --show-toplevel` reported that the supplied working directory
was not a Git repository. Existing scripts, Python implementation, tests,
launchers, configuration, documentation and diagnostic files must be preserved.
The referenced shared `~/.agents/AGENTS.md` and project Mac helper skill are absent.
No other repository's CCE index will be used.

Before editing existing files, preserve their exact bytes and modes in the
ignored `logs/change-backups/2026-11-18-symfony-tooling/` directory (relocated to
`tooling/logs/change-backups/2026-11-18-symfony-tooling/` with the tools).
Do not copy credentials or secret configuration into recovery archives. Existing
private mount settings will be moved unchanged and excluded from Git.
New files and absent paths are recorded in the backup manifest.

## Planned effects and order

1. Create a guarded recovery manifest and snapshot non-secret affected files.
2. Initialize `.git` locally and configure the requested `origin`; inspect remote
   refs without uploading this checkout. Do not publish without explicit request.
3. Inventory existing tool contracts and the explicitly requested `../cdp-cms`
   PHP isolation metadata. Inspect installed PHP/Composer/Valet commands only as
   required for the requested application.
4. Move tool scripts, Python sources/tests, launchers, tool configuration,
   package metadata and tool documentation/logs under `tooling/`. Keep root
   Make targets and agent instructions portable and update affected references.
5. Add a minimal Symfony/Twig application, local static assets, Composer lock,
   application tests and portable PHP 8.3 metadata. Use local storage information
   and a read-only tool catalogue; web requests must not execute cleanup/mounts.
6. Apply PHP 8.3 isolation only to `tools_mac` using the existing Valet pattern.
   Record the prior isolation state and restoration command first.
7. Verify focused relocation and application tests, `make verify`, Composer
   configuration, local HTTP behavior and PHP isolation. Run the tooling health
   check if applicable and report unavailable local integrations honestly.
8. Record disk capacity/used/free and authorized folder totals. No cleanup,
   credential access, global agent setup, service restart or shared-data browsing.

## Risks and checks

Relocation can break path-sensitive wrappers, tests and documentation. Check
entry points from outside the checkout using disposable repository fixtures.
Composer may require public package downloads; do not send private project data.
Valet may require privileged changes; preserve the existing setting and use the
native site-scoped command. Retain all original user data and never follow
escaping symlinks. Recovery refuses later edits instead of overwriting them.

## Numbered rollback procedure

1. Stop only diagnostic processes started by this task; record exact PIDs when
   applicable. There are none at the time of this record.
2. Run the task's guarded rollback script with `--check` before restoration.
   It will compare the final task-owned state against its recorded hashes/modes,
   refuse later edits, and report exact affected paths. Its final path and
   invocation will be recorded below before structural edits.
3. Restore moved tool paths and original bytes/modes from the local recovery
   manifest. Remove only task-created unchanged files after the guard succeeds.
   Restore absent paths to absence; retain the recovery archive and this record.
4. Restore the recorded previous `tools_mac` Valet isolation with the exact
   native command recorded below. Never change the global PHP selection.
5. Remove only this task's local origin configuration if still unchanged. Keep
   `.git` if any later commits/refs exist; never use reset, clean or force push.
6. Verify the original tool entry points and their disposable tests, then review
   the restored path list. Do not overwrite later user work to force rollback.

## Implemented files and native state

- Git was absent; local `main` was initialized and origin set to the requested
  URL. `git ls-remote --symref origin HEAD` returned no refs. No files were pushed.
- Existing scripts, Python implementation/tests, launchers, config, package
  metadata, docs, skills directory and logs moved under `tooling/`. Shell wrappers
  remain location-relative. Root Make shortcuts dispatch there. Agent setup now
  distinguishes the Git root from its tooling/report directory.
- Root Symfony files: `composer.json`, `composer.lock`, `bin/console`, `config/`,
  PHP `src/`, `templates/`, `public/`, application `tests/`, `.php-version`,
  `.valetrc`, README and agent entry-point guidance. No database or Node build.
- New metadata scanner: `tooling/disk-usage.sh` and
  `tooling/src/local_scripts/disk_audit.py`; private saved report:
  `var/storage-audit.json`. No scanned file contents were read, no real cleanup or
  mounts were executed by this task, and denied folders were not retried elevated.
- No generated reports, local mount settings, dependency tree or recovery archive
  are tracked. `tooling/cdp_copy_db.sh` was retained unchanged but ignored because
  it contains credential-related configuration. No secret file was copied into
  the recovery archive. Original private settings were moved, never rewritten.
- Original documentation collided during a transient flattened move; all 14
  original documents were immediately restored from the snapshot into their
  original relative subdirectories under `tooling/docs/` before further edits.

## Storage observations

The whole-Mac scan took 385 seconds. It measured 69 immediate site directories,
totalling about 126.6 GiB of allocated regular-file data. Largest sites:

| Site | Allocated data | Largest top-level area |
| --- | ---: | ---: |
| app_hublist | 54.57 GiB | var: 53.45 GiB |
| cdp-dc | 30.06 GiB | var: 26.55 GiB |
| cdp-cms | 18.22 GiB | var: 14.04 GiB |
| iccxml | 7.15 GiB | I-Codes: 4.18 GiB |

Additional bounded metadata scans of the largest three `var/` directories found
`app_hublist/var/tmp` about 34.73 GiB, `cdp-dc/var/role-privacy-checks` 11.11 GiB,
`cdp-dc/var/runs` 6.22 GiB and `cdp-cms/var/runs` 4.97 GiB. These are observations,
not a deletion allowlist. Saved apps, worktrees, unknown data and dependencies
remain protected by the existing cleaners.

Other measured data included `/opt/homebrew` about 46.22 GiB and `/Applications`
at least 45.71 GiB (including NinjaRMMAgent about 12.72 GiB). Whole-Mac totals
are partial because macOS denied some folders. Site measurements completed
without errors. Cloud/File Provider/credential directories, symlinks and other
filesystems were excluded before enumeration. Allocation totals are not claims
of recoverable physical space on APFS.

The initial data-volume observation was 95% full with about 21 GiB available.
Later live statistics changed during the user's own cleanup/Homebrew activity;
this task claims no measured cleanup savings. The user's pasted output reported
166.9 MiB of selected cache data removed and 1.2 GiB measured free-space increase.
That user-run cleanup is not part of this task's rollback.

## Verification and limitations

- Baseline `make verify`: 104 original tests passed.
- Relocation and scanner tests were run failing before implementation. Final tool
  suite contains 112 tests, including no-content-read, cloud exclusion, hardlink,
  symlink-component, partial-error, ranking and portable-entry-point checks.
- PHP application checks cover missing/malformed/stale reports, invalid sizes,
  live capacity, HTML routes, PHP version, private cache headers, remote-client
  rejection, method restrictions, ignored arbitrary command/path parameters and
  both debug and non-debug kernels. Final application check count: 19.
- Composer install/update succeeded using the site's selected PHP. The final
  installed runtime was verified as PHP 8.3.36 / Symfony 7.4.23. Composer reported
  no vulnerability advisories. Container/Twig/Composer validation passed.
- After changing Symfony major versions, the old non-debug compiled container
  caused HTTP 500 despite debug tests passing. The new non-debug regression
  reproduced the missing service class. The task-created old cache was moved
  intact into `cache-before-php83/` in this recovery archive; rebuilding resolved
  the error. Normal dependency installation now runs Symfony's native cache
  refresh script. The user's saved storage report was retained.
- Browser verification exercised project search/empty results, show-all,
  tool-category/search filters, refresh instructions and mobile navigation with
  no horizontal overflow. No browser console errors. `/health` confirmed
  `{"status":"ok","php":"8.3","symfony":"7.4.23"}` on the temporary preview.
  Screenshot: `tooling/logs/dashboard-preview.jpg`.
- `make check-agent-tools`: Codex CLI, six trusted/enabled native CTX hooks,
  eight skills and local CTX execution/search passed. Exact-root CCE failed:
  no matching local CCE registration. `cce status` separately reports this
  project is not indexed. No other repository's index was used; no global
  registration, package upgrade or full reindex was attempted.
- Valet native inspection/isolation requires interactive sudo and could not
  authenticate from tool execution. The user attempted PHP 8.5 and Valet
  reported it unsupported, prompting the accepted PHP 8.3 correction. The user's
  before-state listing in `tooling/logs/valet-isolation-before.txt` contains no
  `tools_mac` isolated entry. The HTTPS endpoint initially had a hostname
  certificate mismatch; no browser security warning was bypassed. The user was
  asked to run the updated `make valet-isolate` and `valet secure tools_mac`.
  Active Valet isolation and HTTPS remain pending until verified below.

## Exact recovery commands

The original 39 non-secret files and modes are in
`tooling/logs/change-backups/2026-11-18-symfony-tooling/files/`; `before.json`
is the original manifest. `after.json`, `runtime.json`, `relocations.json` and
`git.json` guard the finished state. New paths are the difference between the
before/after manifests. Recovery compares hashes/modes and refuses later edits.

1. Stop only the task-owned PHP preview before recovery. Its latest PID and
   shutdown verification are recorded below. Do not stop Valet or unrelated PHP.
2. From the current checkout, check without mutations:
   `python3 -B tooling/logs/change-backups/2026-11-18-symfony-tooling/recovery.py check`.
3. If it succeeds, restore the original pre-task layout and absent Git state:
   `python3 -B tooling/logs/change-backups/2026-11-18-symfony-tooling/recovery.py restore --archive-git`.
   This restores original source bytes/modes, moves original private settings and
   the legacy helper back, and retains new vendor/runtime files inside recovery.
   Git metadata is moved into the recovery archive only if refs/HEAD/origin still
   match. No reset/clean/delete is used. Omit `--archive-git` to retain Git, but
   review ignored/private data carefully before any later Git add.
4. The recovery archive and diagnostic logs return to root `logs/`. The task
   record remains under `docs/change-records/` for audit. Empty original
   `skills/` is retained. Recovery never overwrites unexpected paths.
5. If the user applied new Valet isolation, restore the recorded original
   unisolated state with `valet unisolate --site=tools_mac` from this checkout.
   Do not change global PHP. TLS repair is a separate user-executed native action;
   no private keys were backed up or rotated by the agent. Review any newly
   created site certificate before choosing native `valet unsecure tools_mac`.
6. Verify the original Python/shell entry points and original `make verify`
   fixture tests. The disk audit deleted nothing and has no data-restoration step.

The guarded recovery procedure was exercised in a disposable repository-local
fixture: it refused later edits before mutation, restored exact bytes/modes and
private relocations, preserved original empty paths and retained generated
runtime data without deletion. No rollback was run on the real checkout.

## Final checks

- Final full `make verify` returned 0: 112 tool tests, 19 PHP checks, shell/Python
  syntax, container wiring, both Twig templates and strict Composer validation.
  `node --check public/assets/app.js` returned 0.
- Compared all 39 original snapshot files to their relocated equivalents:
  30 are byte-identical; nine were intentionally updated for layout/guidance.
  No original file is missing and no original file mode changed.
- Initial staged source review: 74 files, zero private/runtime/credential paths,
  and `git diff --cached --check` returned 0. No remote upload was performed.
- Owned PHP preview PIDs were 71279 (PHP 8.5) and 79648 (PHP 8.3), both stopped
  with targeted TERM signals after their browser checks. They are diagnostic
  processes only; no Valet or unrelated session was stopped.
- The guarded rollback passed disposable restoration/later-edit tests. The
  finished code/runtime/Git guards are sealed after the initial local commit.
- Valet PHP 8.3 isolation and the site certificate repair remain a user-terminal
  step until a successful native command and HTTPS `/health` check are observed.
