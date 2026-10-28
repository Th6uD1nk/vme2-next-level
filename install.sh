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

if [ -z "$PSPDEV" ]; then
  echo "PSPDEV is not set: set up your PSP environment or give its path, for example: PSPDEV=\$HOME/pspdev ./install.sh" >&2
  exit 1
fi

if [ ! -x "$PSPDEV/bin/psp-gcc" ]; then
  echo "psp-gcc was not found in $PSPDEV/bin: check that PSPDEV is the path of your PSP toolchain" >&2
  exit 1
fi

git -C "$root" submodule update --init

mkdir -p "$root/me-core-mapper/build"
(cd "$root/me-core-mapper/build" && PATH="$PSPDEV/bin:$PATH" cmake .. && PATH="$PSPDEV/bin:$PATH" make)

remove_block
{
  echo "$begin"
  echo "export VMEGC_HOME=\"$root\""
  echo "export PATH=\"\$VMEGC_HOME/bin:\$PATH\""
  echo "$end"
} >> "$rc"

echo "vmegc installed: open a new terminal, or run: . $rc"
