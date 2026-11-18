# Local tools dashboard

Build a small local Symfony 7.4 LTS application on PHP 8.3 at `tools_mac.test`.
The user changed the initial PHP 8.5 requirement after the installed Valet
reported that it does not support PHP 8.5. Do not upgrade global Valet tooling.
The requested first screen combines real disk statistics, the largest projects
under the sibling sites directory, and a catalogue of the existing local tools.

Use Symfony with Twig, a small local CSS/JavaScript layer, and no Node build,
database, external fonts, analytics, AI provider or hosted storage. The visual
direction is a modern assistant workspace: quiet graphite sidebar, cool light
canvas, clear tool search, an explanatory storage insight, and a ranked project
table. Palette: canvas #f6f7f9, surface #ffffff, ink #20232b, muted #68717f,
accent #4659ce, warning #a95516. Use the native system sans-serif stack and
tabular numerals. All content aligns left, with an accessible mobile drawer.

Choose server-rendered Symfony over a separate SPA: it provides the requested
PHP application with fewer dependencies and no second runtime. Browser requests
read a saved local JSON audit and live filesystem capacity; expensive traversal
runs only through an explicit CLI refresh. No web route executes shell commands,
cleanup, mounts or arbitrary user-supplied paths. The browser offers command
copying, search and ranked lists. There is no simulated AI chat.

All original tooling moves to `tooling/`, including its Python sources, tests,
configuration, launchers, documentation and reports. Root Make targets dispatch
to that directory. Derive checkout paths from script locations and Symfony's
`kernel.project_dir`; derive the default sites path from the checkout parent.
Allow explicit sites-directory configuration for non-Valet layouts.

Disk scanning is metadata-only, same-filesystem, does not follow symlinks, excludes
cloud/File Provider paths, network mounts and credential stores, and records
permission denials/incomplete results. The user authorized the whole local Mac.
Rank immediate site project directories using allocated file bytes and label
incomplete totals. Never browse mounted shares or read file contents.

Verify migration with the existing disposable fixture tests, add tests for scan
boundaries and stale/malformed reports, verify Symfony routes and PHP requirements,
then run `make verify`. Preserve original bytes and modes in local ignored
recovery data. Do not publish or change global PHP/agent configuration.
