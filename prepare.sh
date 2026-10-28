#!/bin/sh
set -e

root=$(dirname "$(readlink -f "$0")")

if [ -z "$PSPDEV" ]; then
  echo "PSPDEV is not set: set up your PSP environment or give its path, for example: PSPDEV=\$HOME/pspdev ./prepare.sh" >&2
  exit 1
fi

if [ ! -x "$PSPDEV/bin/psp-gcc" ]; then
  echo "psp-gcc was not found in $PSPDEV/bin: check that PSPDEV is the path of your PSP toolchain" >&2
  exit 1
fi

for submodule in me-core-mapper me-vme-samples; do
  state=$(git -C "$root" submodule status "$submodule" 2>/dev/null | cut -c1)
  if [ "$state" = "-" ]; then
    git -C "$root" submodule update --init "$submodule"
  elif [ "$state" = "+" ]; then
    echo "warning: $submodule is not on the commit recorded by the project, it is left as it is" >&2
  fi
done

if [ ! -f "$root/me-core-mapper/CMakeLists.txt" ]; then
  echo "me-core-mapper is empty: clone the project with its submodules (git submodule update --init)" >&2
  exit 1
fi

build="$root/me-core-mapper/build"
mkdir -p "$build"
cd "$build"
if [ ! -f CMakeCache.txt ]; then
  PATH="$PSPDEV/bin:$PATH" cmake ..
fi
PATH="$PSPDEV/bin:$PATH" make
