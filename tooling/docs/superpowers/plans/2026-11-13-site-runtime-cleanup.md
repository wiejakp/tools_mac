# Site Runtime Cleanup Implementation Plan

> Execute inline with the executing-plans workflow; no delegation or commits.

**Goal:** Existing cache/log commands include the generated outputs responsible
for app_hublist disk growth while retaining protected project and application data.

**Architecture:** Preserve active-app discovery and descriptor-based deletion.
A separate metadata-only, descriptor-based traversal examines selected runtime
roots, recognizes generated output by multiple markers, and adds narrow targets.
CACHE/LOGS filtering and the existing preview/confirmation flow stay centralized.

**Tech stack:** Python standard library, Python >=3.9, POSIX shell, unittest.

**Spec:** [Scope, evidence and rollback](../../change-records/2026-11-13-site-runtime-cleanup.md).

## Constraints and review focus

- No real cleanup, app execution, dependencies, network or global changes.
- Preserve unknown files, uploads/data, source fixtures, archived apps and links.
- Cache cleanup includes generated coverage; log cleanup includes loose/rotated
  runtime logs. Each must preserve the other kind.
- Recognition needs regular, non-symlink evidence. Reject changed target identity.
- An isolated test runtime may be traversed only with parent/exit metadata and
  a reports directory; an ordinary test/fixture tree remains protected.

## Task 1: Recognized generated outputs

Files: src/local_scripts/sites_cleaner.py, tests/test_sites_cleaner.py.

- [x] Add failing tests for paired PHPUnit outputs/worker shards, HTML coverage,
      compiled Symfony caches and standard .phpunit-coverage.
- [x] Add boundary tests for cache/log separation, dry-run, lookalikes, fixtures,
      archived apps, protected data, symlinks and replaced target identity.
- [x] Run focused tests and confirm missing-behavior failures.
- [x] Implement narrow runtime discovery and target identity checks.
- [x] Run focused tests; inspect every failure before continuing.

## Task 2: Document and verify

Files: README.md, AGENTS.md, change record and this plan.

- [x] Document expanded cleanup, confirmation/preview usage and preserved data.
- [x] Run make verify and git --no-pager diff --check after final source edits.
- [x] Check new runtime discovery read-only against the requested app with a
      strict time budget; report coverage and any limit without deleting files.
- [x] Validate rollback restoration/refusal in disposable fixtures.
- [x] Save final file hashes/modes, verification and exact rollback command.
- [x] Refresh only changed source/test CCE paths and reconcile this checklist.

## Completion reconciliation

All requested implementation and verification items are complete. Final make verify
exited 0 with 90 tests; the read-only app discovery found 42.96 GiB in selected
coverage files, and exact rollback/refusal fixtures passed. No app cleanup ran.
Source/test CCE refreshes exited 0 and index status is operational.
