#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
DIST_DIR="$ROOT_DIR/packaging/dist"
mkdir -p "$DIST_DIR"
TARBALL="$ROOT_DIR/packaging/rpm/gravador-cdrdao-0.1.0.tar.gz"
( cd "$ROOT_DIR" && tar -czf "$TARBALL" --exclude packaging/dist --exclude .venv . )

rpmbuild -ta "$TARBALL"
RPM_PATH=$(find "$HOME/rpmbuild/RPMS" -name "gravador-cdrdao-0.1.0-1.noarch.rpm" | head -n 1)
cp "$RPM_PATH" "$DIST_DIR/"
