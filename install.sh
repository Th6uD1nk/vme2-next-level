#!/bin/sh
set -e

root=$(dirname "$(readlink -f "$0")")
rc="$HOME/.bashrc"
begin="# vmegc begin"
end="# vmegc end"

remove_block() {
  if [ -f "$rc" ] && grep -qxF "$begin" "$rc"; then
    sed -i "/^$begin\$/,/^$end\$/d" "$rc"
  fi
}

if [ "$1" = "--uninstall" ]; then
  remove_block
  echo "vmegc removed from $rc"
  exit 0
fi

"$root/prepare.sh"

remove_block
{
  echo "$begin"
  echo "export VMEGC_HOME=\"$root\""
  echo "export PATH=\"\$VMEGC_HOME/bin:\$PATH\""
  echo "$end"
} >> "$rc"

echo "vmegc installed: open a new terminal, or run: . $rc"
