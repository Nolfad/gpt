#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
BUILD_DIR="$ROOT_DIR/packaging/debian/build"
DIST_DIR="$ROOT_DIR/packaging/dist"
mkdir -p "$BUILD_DIR" "$DIST_DIR"
rsync -a --delete "$ROOT_DIR/" "$BUILD_DIR/" --exclude packaging/debian/build --exclude packaging/dist --exclude .venv
cd "$BUILD_DIR"
dpkg-buildpackage -us -uc
mv ../*.deb "$DIST_DIR/gravador-cdrdao_0.1.0_all.deb"
