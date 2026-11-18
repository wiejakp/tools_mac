PYTHON ?= /usr/bin/python3
PHP := ./tooling/php.sh
CODEX ?= codex
AGENT ?= agent
GEMINI ?= gemini

.PHONY: help codex agent gemini clear cache logs clear-cache clear-logs mount mount-home mount-cch test check verify preview-logs preview-cache preview-mounts
.PHONY: check-agent-tools audit audit-mac app-test install console valet-isolate serve

help:
	@printf '%s\n' 'make install        Install locked Symfony dependencies with site PHP' 'make valet-isolate  Select the site PHP version from .valetrc' 'make audit          Rank the sibling site projects' 'make audit-mac      Read-only local Mac storage report' 'make serve          Preview at http://127.0.0.1:8080' 'make console ARGS=  Run the Symfony console'
	@printf '%s\n' 'make check-agent-tools  Check native Codex hooks and local CCE/CTX'
	@printf '%s\n' 'make codex          Codex chat list with automatic approval review' 'make agent          Cursor Agent in this project' 'make gemini         Gemini CLI in this project' 'make clear cache    Interactive cache cleanup (also clear-cache)' 'make clear logs     Interactive log cleanup (also clear-logs)' 'make preview-cache  Preview cache cleanup' 'make preview-logs   Preview log cleanup' 'make mount          Interactive work and home mounting' 'make mount-home     Interactive home mounting' 'make mount-cch      Interactive CCH mounting' 'make preview-mounts Preview configured mounts without connecting' 'make verify         Syntax and disposable fixture tests'

check-agent-tools:
	./tooling/agent-setup.sh --check-tools

codex:
	@"$(CODEX)" --cd "$(CURDIR)" --strict-config \
		--sandbox workspace-write --ask-for-approval on-request \
		--config 'approvals_reviewer="auto_review"' \
		--config sandbox_workspace_write.network_access=true \
		--enable guardian_approval --enable hooks --enable plugin_hooks agents

agent:
	@"$(AGENT)"

gemini:
	@"$(GEMINI)"

clear:
ifeq ($(filter cache logs,$(MAKECMDGOALS)),)
	@printf '%s\n' 'Choose: make clear cache | make clear logs'
else
	@:
endif

cache clear-cache:
	./tooling/clear-cache.sh

logs clear-logs:
	./tooling/clear-logs.sh

mount:
	./tooling/mount.sh

mount-home:
	./tooling/mount-home.sh

mount-cch:
	./tooling/mount-cch.sh

test:
	$(PYTHON) -B -m unittest discover -s tooling/tests -v

check:
	@for script in tooling/*.sh tooling/launchers/*.command; do /bin/sh -n "$$script" || exit; done
	$(PYTHON) -B -c "import ast; from pathlib import Path; files = list(Path('tooling/src').rglob('*.py')) + list(Path('tooling/tests').glob('*.py')); [ast.parse(p.read_text(), filename=str(p)) for p in files]; print('Python syntax: OK')"

verify: check test app-test

preview-logs:
	./tooling/clear-logs.sh --dry-run

preview-cache:
	./tooling/clear-cache.sh --dry-run

preview-mounts:
	./tooling/mount.sh --dry-run

audit:
	./tooling/disk-usage.sh

audit-mac:
	./tooling/disk-usage.sh --whole-mac

install:
	$(PHP) "$$(command -v composer)" install --no-interaction

console:
	$(PHP) bin/console $(ARGS)

app-test:
	$(PHP) tests/run.php
	$(PHP) bin/console lint:container
	$(PHP) bin/console lint:twig templates
	$(PHP) "$$(command -v composer)" validate --strict --no-check-publish

valet-isolate:
	@mkdir -p tooling/logs
	valet isolated > tooling/logs/valet-isolation-before.txt
	valet isolate "$$(sed -n 's/^php=//p' .valetrc)" --site=tools_mac

serve:
	$(PHP) -S 127.0.0.1:8080 -t public public/router.php
