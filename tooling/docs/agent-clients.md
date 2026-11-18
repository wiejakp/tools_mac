# Coding clients and local agent tooling

## Start a client

From this Git repository:

```sh
make codex
make agent
make gemini
```

These remain direct native CLI recipes, matching the existing app_hublist
pattern. `CODEX`, `AGENT` and `GEMINI` can select an installed executable, for
example `make codex CODEX=/absolute/path/to/codex`. Choose the provider yourself;
configuration and skills do not authorize sending private data to another AI
service. This repair does not start Cursor/Gemini or install their clients.

All clients must use local CCE for repository retrieval and local context-mode
(CTX) for substantial output and available session memory. Verify the exact
`git rev-parse --show-toplevel` root before retrieval. Never borrow another
project's CCE index, use hosted analysis or index credentials.

## Check the current repository

```sh
make check-agent-tools
```

Equivalent from another Git working directory:

```sh
/path/to/checkout/tooling/agent-setup.sh --check-tools
```

The check uses native configuration and bounded local stdio processes. It checks:

- Native Codex configuration and six enabled/trusted global CTX hooks.
- The eight required CTX skills in native skill discovery.
- The CCE server whose `--project-dir` matches this exact Git root, its operational
  index and a small semantic search.
- Actual CTX JavaScript execution and its search interface. An empty knowledge
  base is reported as empty; it is normal before any content is indexed.

It prints PASS/FAIL directly, returns 0 only when all checks pass, and returns 1
for failures. It changes no configuration, starts no model turn, never probes
another project's CCE or an HTTP MCP endpoint, and closes only its own processes.
Local MCPs may record ordinary diagnostic session statistics. No artificial
content is added to the knowledge base and no index is purged/rebuilt.

Run this after runtime/configuration updates and whenever tooling fails. In a
restricted execution sandbox, Codex's state database or CTX session directory
may be unavailable. Run the same check in normal Terminal, or through an already
authorized native diagnostic; do not expand repository/cloud permissions or
request CCE/CTX tool access approvals to hide that boundary.

## Global Codex hook configuration

Codex supports native user hooks in `~/.codex/hooks.json`, independent of plugin
hooks and project trust. See [official OpenAI hook documentation](https://learn.chatgpt.com/docs/hooks).

This Mac now registers PreToolUse, PostToolUse, SessionStart, PreCompact,
UserPromptSubmit and Stop there. Each invokes the installed local Node and CTX
CLI with a 20-second timeout and a runtime PATH prefix. Absolute runtime paths
support GUI startup without requiring an interactive NVM shell. The local CTX
MCP uses that same Node/CLI installation and keeps its cwd dynamic, so each client
starts it from the active repository. Routine tool approval policies are retained.

The old `context-mode@context-mode` cached-plugin registration is retired. The
replacement preserves lifecycle functionality, local MCP and skills. Codex no
longer needs to package npm-managed `node_modules/.bin` entries for these hooks;
future dependency relinking does not affect this native hook registration.

The canonical `~/.agents/skills/context-mode` tree contains physical files,
copied byte-for-byte with modes from the existing library. It no longer links
to a particular plugin-cache version. Other personal skills are untouched.

Trust was set once through native Codex APIs using only the six hashes returned
by native `hooks/list`. No trust-bypass flag or invented hash is used. Review
changed hook commands through Codex's native `/hooks` interface. Keep only one
active registration; enabling the old plugin as well can duplicate hooks.

Already-running sessions can retain an older hook registry. Reopen the affected
Codex session once after migration. The existing daemon's control-socket reload
timed out during this repair; other active sessions were preserved. Fresh CLI
and managed-runtime hook discovery/trust and all six isolated handler executions
were verified. Metadata-only startup probes emitted no native lifecycle run
events, so those probes are not claimed as end-to-end model-turn verification.

`project_doc_max_bytes = 65536` accommodates the observed combined instruction
size and clears the native truncation warning without removing safety guidance.

## Install CCE and CTX when missing

Both are already installed on this Mac. The following are installation steps,
not commands to rerun against a healthy setup. Take a local configuration backup
and write exact rollback steps before installation/registration changes.

With an existing Node installation, the installed CTX package requires Node
22.5 or newer:

```sh
npm install -g context-mode
```

Use the [context-mode project documentation](https://github.com/mksglu/context-mode)
for the selected version. Register local stdio, using absolute installed runtime
paths for GUI use. Native Codex hooks dispatch through
`context-mode hook codex <event>`; do not copy a dependency-filled npm directory
into a hook plugin just to register those commands. After a Node version change,
update the pinned MCP/hook runtime paths, review native hook trust and rerun the
health check. No unattended upgrades or background repair jobs are installed.

CCE's local installation uses its local embedding extra:

```sh
uv tool install 'code-context-engine[local]'
```

Follow [CCE installation and agent guidance](https://elara-labs.github.io/code-context-engine/guide/agents/overview/).
From the intended Git root, review secret/ignored-path exclusions before first
initialization. `cce init --agent codex` initializes that project and registers its
local stdio server. First installation/indexing can require public dependency or
model downloads; diagnostic runs keep Hugging Face/Transformers offline.

For a healthy existing index, refresh only changed paths:

```sh
cce index --path /absolute/repository/changed-file.py
```

A stale MCP transport does not prove index corruption. Reconnect/reopen the
correct client before considering index repair; do not full-reindex routinely.

## Project configuration and recovery

The copied checkout does not contain the former `.cursor/`, `.gemini/` or
project skill configuration. Do not assume their historical registrations are
active. Keep client cwd rooted in the current checkout (native cwd or an
explicit invocation argument), then verify CCE's project root against
`git rev-parse --show-toplevel`. Never retain another machine's absolute path.
Root `GEMINI.md` points to the tooling guidance. Global client settings are not
changed by the Symfony migration. Skills grant no extra Mac, network, cloud,
credential or provider access.

The [tooling change record](change-records/2026-11-13-agent-tooling.md) contains
exact affected paths, preserved original bytes/modes, native verification,
limitations and a guarded rollback. Recovery stays in ignored
`logs/change-backups/2026-11-13-agent-tooling/`. Rollback refuses later edits and
restores this task's original state, including prior cache-cleaner work. It
intentionally restores the old broken plugin selection if fully reversed.
