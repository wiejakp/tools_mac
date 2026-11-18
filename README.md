# Tools for your Mac

A local Symfony 7.4 LTS dashboard for disk statistics, the largest site projects and
everyday Mac tools. It runs at [tools_mac.test](https://tools_mac.test).
The dashboard has project search, expandable size breakdowns, tool filters and
commands to copy into Terminal. All assets and reports stay local.

## Run the application

PHP **8.3** is selected in `.valetrc`, following the sibling `cdp-cms` project's
Valet pattern. `.php-version` and Composer's PHP platform agree with it. The
default PHP on your Mac is unchanged.

From this checkout:

```sh
make install
make valet-isolate
make audit-mac
```

Valet may ask for your Mac administrator password in Terminal. `make
valet-isolate` reads the version from `.valetrc` and affects this site only. Open [the dashboard](https://tools_mac.test)
after the command succeeds. If the site was already secured in Valet, its HTTPS
configuration is reused. The `/health` endpoint reports the PHP version actually
serving the request; `.valetrc` alone is not proof of active isolation.

`make serve` provides an optional PHP 8.3 preview at
[localhost:8080](http://127.0.0.1:8080). Stop it with Ctrl-C. Use
`TOOLS_PHP_BINARY=/path/to/php` when PHP 8.3 is installed outside Homebrew.
The PHP wrapper checks the selected major/minor version before running anything.

## Storage reports

```sh
make audit            # Rank projects in the parent of this checkout
make audit-mac        # Also inspect local user, app and system-data folders
./tooling/disk-usage.sh --help
./tooling/disk-usage.sh --sites-root /path/to/sites
```

The scanner reads file metadata without reading file contents or deleting data.
It does not follow symlinks or cross filesystems. It excludes cloud/File Provider
folders, credential stores and mounted shares. Denied or timed-out folders are
marked partial; no permission escalation is attempted. The default time budget
is 600 seconds, configurable with `--max-seconds`.

Folder sizes count allocated regular-file bytes and deduplicate hardlinks within
each directory measurement. APFS clones, shared volumes, snapshots and reserved
space can make these differ from physical volume usage. The dashboard's live
volume statistic labels capacity minus available space as **used & reserved**.
The saved JSON report is private, ignored by Git and stored at
`var/storage-audit.json`; remove it to clear the dashboard's project data.

Reports can be stale or incomplete; the dashboard labels both. Expensive scans
run explicitly in Terminal. Web requests read the report, never execute tools,
and only accept loopback clients. Commands for cleanup open the existing
interactive menus or previews and retain their original confirmation behavior.

## Project layout

```text
bin/console          Symfony console
config/              Symfony configuration
public/              Front controller and local CSS/JavaScript
src/                 Symfony application
templates/           Twig views
tests/               Application behavior checks
tooling/             Personal scripts, Python code/tests, launchers and tool docs
var/                 Ignored runtime files and private storage report
```

Project paths come from the checkout or script location. The default sites root
is the checkout's parent; there are no hardcoded user/Desktop paths in active
configuration. Existing tools and private mount settings now live under
`tooling/`. See [the tooling guide](tooling/README.md) for their individual
contracts. Root Make shortcuts remain available:

```sh
make help
make preview-cache
make preview-logs
make mount
make check-agent-tools
make verify
```

`make verify` checks shell/Python syntax, disposable cleanup/mount/storage tests,
application behavior, service wiring, Twig syntax and Composer configuration.
Fixtures never touch real apps or network shares.

The Git origin is `https://github.com/wiejakp/tools_mac.git`. Private reports,
local settings, recovery data, dependencies and the legacy database helper are
excluded from Git. The helper is retained locally under `tooling/` because it
contains credential-related configuration and needs a separate review before
publication.

Agent workflow: [AGENTS.md](AGENTS.md). Migration and guarded rollback:
[change record](docs/change-records/2026-11-18-symfony-tooling.md).
