# Local dashboard implementation plan

> Execute natively in this checkout, one task at a time.

**Goal:** A portable Symfony dashboard showing storage, largest sites and tools.

**Architecture:** Twig pages read a local audit report and live capacity. A
metadata-only Python CLI produces the audit. Existing independent tools remain
CLI-only under `tooling/`.

**Tech stack:** PHP 8.3, Symfony 7.4 LTS, Twig, native CSS/JS, Python standard library.

**Spec:** `docs/superpowers/specs/2026-11-18-local-dashboard-design.md`.

## Constraints and review focus

- No hardcoded user or Desktop checkout paths.
- Never follow symlinks, inspect cloud/mounted shares, or read scanned contents.
- Report partial permission-denied scans and missing/stale report data honestly.
- No web shell execution, arbitrary path scanning or destructive actions.
- Preserve all original tool behavior, private settings and rollback information.

## Task 1: Portable tool migration

- [x] Preserve bytes/modes and record Git/Valet state before mutation.
- [x] Run existing fixture tests as baseline; add a relocation smoke test.
- [x] Move existing tools, sources, tests, launchers, settings and docs to tooling.
- [x] Update root Make dispatch, agent instructions and active documentation.
- [x] Verify original tool fixture tests and entry points from another cwd.

## Task 2: Metadata-only storage audit

- [x] Add failing fixtures for symlinks, cloud exclusions, project ranking,
  hardlinks, partial errors and portable default roots.
- [x] Implement `tooling/src/local_scripts/disk_audit.py` and its shell entry point.
- [x] Produce versioned JSON with volume capacity, bounded local directory totals,
  biggest sites, elapsed time and incompleteness counts; save under root var.
- [x] Run the authorized read-only whole-Mac audit and inspect bounded summaries.

## Task 3: Symfony dashboard and local PHP

- [x] Add Composer dependencies, kernel/config, Twig templates and local assets.
- [x] Add report-reader tests for absent/malformed data and kernel route checks.
- [x] Implement the read-only dashboard, tools catalogue, project search/sort,
  refresh instructions and truthful empty/error states.
- [x] Add `.php-version`, `.valetrc` and a portable PHP 8.3 command wrapper.
- [ ] Apply native site PHP isolation if authorized tooling permits it; verify
  HTTP PHP runtime and preserve the previous isolation state.
- [x] Run `make verify`, Composer validation and local HTTP/browser checks.
- [x] Review staged files for privacy, seal the recovery guard, and update the
  task record with actual results and any external step still required.
