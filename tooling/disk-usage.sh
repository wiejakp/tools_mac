#!/bin/sh
# Metadata-only storage report, portable across checkouts.
set -eu
tooling_dir=$(cd -P -- "$(dirname -- "$0")" >/dev/null && pwd -P)
exec /usr/bin/python3 -B "$tooling_dir/src/local_scripts/disk_audit.py" "$@"
