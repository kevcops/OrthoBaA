#!/usr/bin/env bash
set -euo pipefail

APP_ID="ipa-fixer"
APP_NAME="IPA Fixer – Before & After"
ICON_SRC="assets/Icons/ipa-fixer-dark-512.png"
DESKTOP_SRC="assets/Icons/repo-snippets/ipa-fixer.desktop"
APPRUN_SRC="assets/Icons/repo-snippets/AppRun"

if [ ! -f "$ICON_SRC" ]; then
  echo "Icon not found: $ICON_SRC" >&2
  exit 1
fi

python3 -m pip install --upgrade pyinstaller

# Build standalone binary
pyinstaller --noconfirm --onefile --windowed --name "$APP_ID" \
  --add-data "assets/Icons/ipa-fixer-dark-512.png:assets/Icons" \
  ortho_baa/main.py

OUT_DIR="build/appimage"
APPDIR="$OUT_DIR/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/icons/hicolor/512x512/apps"

cp "dist/$APP_ID" "$APPDIR/usr/bin/$APP_ID"
cp "$ICON_SRC" "$APPDIR/$APP_ID.png"
cp "$ICON_SRC" "$APPDIR/usr/share/icons/hicolor/512x512/apps/$APP_ID.png"

# Desktop file (update name if needed)
cp "$DESKTOP_SRC" "$APPDIR/$APP_ID.desktop"
# Replace Name line to match full app name
sed -i "s/^Name=.*/Name=$APP_NAME/" "$APPDIR/$APP_ID.desktop"

# AppRun
cp "$APPRUN_SRC" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

if [ -z "${APPIMAGETOOL:-}" ]; then
  if [ -x /tmp/appimagetool.AppImage ]; then
    APPIMAGETOOL="/tmp/appimagetool.AppImage"
  else
    APPIMAGETOOL="appimagetool"
  fi
fi

if [ -x "$APPIMAGETOOL" ]; then
  "$APPIMAGETOOL" "$APPDIR" "$OUT_DIR/${APP_ID}.AppImage"
  exit 0
fi

if command -v "$APPIMAGETOOL" >/dev/null 2>&1; then
  "$APPIMAGETOOL" "$APPDIR" "$OUT_DIR/${APP_ID}.AppImage"
  exit 0
fi

echo "appimagetool not found. Install it, then run:" >&2
echo "  appimagetool $APPDIR" >&2
exit 2
