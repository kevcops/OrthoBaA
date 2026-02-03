
#!/usr/bin/env bash
set -euo pipefail

APP_ID="ortho-baa"
APP_NAME="Ortho Before and After"
APP_DIR="${HOME}/.local/share/applications"
BIN_DIR="${HOME}/.local/bin"
ICON_DIR="${HOME}/.local/share/icons"

mkdir -p "${APP_DIR}" "${BIN_DIR}" "${ICON_DIR}"

# Install icon
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "${SCRIPT_DIR}/assets/Icons/ipa-fixer-dark-512.png" "${ICON_DIR}/${APP_ID}.png"

# Launcher script
cat > "${BIN_DIR}/${APP_ID}" <<'LAUNCH'
#!/usr/bin/env bash
exec python3 -m ortho_baa.main "$@"
LAUNCH
chmod +x "${BIN_DIR}/${APP_ID}"

# Desktop entry
cat > "${APP_DIR}/${APP_ID}.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Exec=${BIN_DIR}/${APP_ID}
Icon=${APP_ID}
Terminal=false
Categories=Graphics;Office;
StartupNotify=true
DESK

echo "Installed desktop entry at ${APP_DIR}/${APP_ID}.desktop"
echo "If it doesn't appear immediately, try: update-desktop-database || true; xdg-desktop-menu forceupdate || true"
