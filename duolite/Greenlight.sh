#!/bin/bash
set -eu
app_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$app_dir/greenlight/launcher.py"
