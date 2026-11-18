#!/bin/sh
# Use this site's PHP version without changing global PHP or hardcoding a user.
set -eu
project_dir=$(cd -P -- "$(dirname -- "$0")/.." >/dev/null && pwd -P)
version=$(sed -n 's/^php=php@\([0-9][0-9.]*\)$/\1/p' "$project_dir/.valetrc")
if [ -z "$version" ]; then
    printf '%s\n' 'Set php=php@8.3 in .valetrc.' >&2
    exit 1
fi
candidate=${TOOLS_PHP_BINARY:-}
if [ -z "$candidate" ] && command -v brew >/dev/null 2>&1; then
    brew_prefix=$(brew --prefix)
    candidate="$brew_prefix/opt/php@$version/bin/php"
fi
if [ ! -x "$candidate" ]; then
    candidate=$(command -v php || true)
fi
if [ -z "$candidate" ] || [ "$("$candidate" -r 'echo PHP_MAJOR_VERSION,".",PHP_MINOR_VERSION;')" != "$version" ]; then
    printf 'PHP %s is required. Set TOOLS_PHP_BINARY to its executable.\n' "$version" >&2
    exit 1
fi
exec "$candidate" "$@"
