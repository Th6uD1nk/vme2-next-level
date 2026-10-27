#!/bin/bash

set -e

cd "$(dirname "$0")"

for dir in */; do
  dir="${dir%/}"
  if [ ! -f "$dir/CMakeLists.txt" ]; then
    continue
  fi
  echo "Building: $dir"
  mkdir -p "$dir/build"
  find "$dir/build" -maxdepth 1 -type f ! -name "usbhostfs_pc" -delete
  (cd "$dir/build" && cmake .. && make -j"$(nproc)")
done

echo "All samples built successfully"
