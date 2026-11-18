#!/bin/bash

set -e

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../../.." && pwd)"

python3 "$root/vmeemu.py" --verbose --run logic-add --buffers-words 4 "$here/logic-add.vmeg.c" "$@"
