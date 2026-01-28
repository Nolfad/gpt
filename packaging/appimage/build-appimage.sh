#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
APPDIR="$ROOT_DIR/packaging/appimage/AppDir"
DIST_DIR="$ROOT_DIR/packaging/dist"
mkdir -p "$APPDIR" "$DIST_DIR"

pip install --upgrade pip
pip install -e "$ROOT_DIR" --prefix="$APPDIR/usr"

install -D -m 0644 "$ROOT_DIR/resources/gravador-cdrdao.desktop" "$APPDIR/usr/share/applications/gravador-cdrdao.desktop"
install -D -m 0644 "$ROOT_DIR/resources/gravador-cdrdao.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/gravador-cdrdao.svg"
install -D -m 0755 "$ROOT_DIR/resources/gravador-cdrdao-helper" "$APPDIR/usr/libexec/gravador-cdrdao-helper"
install -D -m 0644 "$ROOT_DIR/resources/br.com.gravadorcdrdao.policy" "$APPDIR/usr/share/polkit-1/actions/br.com.gravadorcdrdao.policy"

linuxdeploy --appdir "$APPDIR" \
  --desktop-file "$APPDIR/usr/share/applications/gravador-cdrdao.desktop" \
  --icon-file "$APPDIR/usr/share/icons/hicolor/scalable/apps/gravador-cdrdao.svg" \
  --output appimage

mv Gravador*.AppImage "$DIST_DIR/gravador-cdrdao-0.1.0.AppImage"
