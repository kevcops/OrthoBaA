
# IPA Fixer – Before & After (Qt)

Drag-and-drop desktop app for creating printable **Before & After** comparisons as **PDF** or **JPEG**.  
Optional per-image crop, batch mode, preview, status bar, and config persistence.

## Features
- Drag & drop **Before** (left) and **After** (right)
- **Optional crop** per image (top-crop + bottom-anchored final height)
- Export **PDF** (landscape letter) or **side-by-side JPEG**
- **Preview** opens the exported file automatically
- **Batch mode**: process a folder of pairs (`*_before.*` + `*_after.*` or alphabetic pairing)
- **Status bar + progress**
- Remembers last output folder and format (`~/.config/ortho_baa/config.json`)
- Extra formats: **HEIC/AVIF/WEBP** (via `pillow-heif`)

## Install & Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 -m ortho_baa.main
# or: python3 ortho_baa/main.py
```

## Build one-click apps (local)
### Windows
```bat
build_win.bat
```
Artifacts: `dist\OrthoBaA.exe`

### macOS
```bash
chmod +x build_mac.sh
./build_mac.sh
```
Artifacts: `dist/OrthoBaA.app` and `dist/OrthoBaA-macOS.zip`

## CI (GitHub Actions)
Tag a release to build and attach binaries:
```bash
git tag v0.1.0
git push origin v0.1.0
```

## License
MIT
