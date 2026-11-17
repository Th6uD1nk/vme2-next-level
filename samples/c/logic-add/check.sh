#!/bin/bash

set -e

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../.." && pwd)"
work="${TMPDIR:-/tmp}/vmegt-logic-add"
log="$work/results.log"

status=0
python3 "$root/vmegt.py" --check --buffers-words 4 --work "$work" --log "$log" "$here/logic-add.vmeg.c" "$@" || status=$?
if [ -f "$log" ]; then
  cat "$log"
fi
exit $status
