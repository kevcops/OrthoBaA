
#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --windowed --name OrthoBaA ortho_baa/main.py
echo "Zipping .app bundle…"
ditto -c -k --sequesterRsrc --keepParent "dist/OrthoBaA.app" "dist/OrthoBaA-macOS.zip"
echo "Done. See dist/OrthoBaA.app and dist/OrthoBaA-macOS.zip"
