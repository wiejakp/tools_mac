# Global Agent Tooling Implementation Plan

> Execute inline using the existing debugging, planning and verification workflows.

**Goal:** Restore native global CTX hooks, preserve local CCE/CTX retrieval and
provide a fast, repeatable health check without a custom agent launcher.

**Architecture:** Native ~/.codex/hooks.json invokes the installed CTX runtime.
The existing helper gains bounded stdio diagnostics; existing Make launch recipes
remain direct. Native Codex APIs supply and verify trust hashes.

**Stack:** Python >=3.9 standard library, local Node/CTX/CCE, native Codex JSON-RPC.

**Spec:** [Scope and reversible migration](../../change-records/2026-11-13-agent-tooling.md).

- [x] Back up exact project/global bytes, modes and absent paths; prepare commands.
- [x] Add failing tests for bounded JSON-RPC, trusted native hooks, local-only MCP
      matching, real execution output validation and health failure exit codes.
- [x] Implement helper and make check-agent-tools; keep launch recipes direct.
- [x] Install native global hooks and precise native config edits with guards.
- [x] Trust only native-reported hashes; verify both native runtime versions.
      Running-daemon proxy reload timed out; existing sessions may need reopening.
- [x] Verify six isolated handler executions, native hook trust/discovery, local
      CTX and exact-root CCE retrieval/skills. Metadata-only probes emitted no
      native lifecycle events; a model-turn lifecycle test was not performed.
- [x] Document setup, health, update expectations and tested guarded rollback.
- [x] Run make verify (104 tests), health/diff checks and targeted CCE refresh;
      capture final descriptors as the last recovery step.
