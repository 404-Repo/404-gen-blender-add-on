#!/usr/bin/env bash
set -euo pipefail

DEST_DIR="./fourofour_3d_gen/wheels"
mkdir -p "$DEST_DIR"

PLATFORMS=(
  "macosx_11_0_arm64"
  "win_amd64"
  "manylinux2014_x86_64"
)

PYTHON_VERSION="3.11"
IMPLEMENTATION="cp"   
ABI="cp311"

PACKAGES=(
  "mixpanel==4.10.1"
  "pydantic==2.11.7"
)

for pkg in "${PACKAGES[@]}"; do
  for plat in "${PLATFORMS[@]}"; do
    echo ">>> Downloading $pkg for $plat (Python $PYTHON_VERSION)"
    pip download \
      --dest "$DEST_DIR" \
      --only-binary=:all: \
      --platform "$plat" \
      --python-version "$PYTHON_VERSION" \
      --implementation "$IMPLEMENTATION" \
      --abi "$ABI" \
      "$pkg"
  done
done

echo "All wheels downloaded into $DEST_DIR/"
