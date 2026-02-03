
# IPA Fixer – Before & After (Qt)

Drag-and-drop desktop app for creating printable **Before & After** comparisons as **PDF** or **JPEG**.

## Highlights
- **Clean UI** – only the drag-and-drop panes have dashed borders.
- **Live filename updates** – suggested name refreshes when you toggle **ID / First / Last** and after both images are set.
- **Preview & Go-to-folder** – preview the output and jump straight to the folder after save.
- **Batch mode** – process a folder of pairs.
- **HEIC/AVIF/WEBP** – supported via `pillow-heif` if installed.
- **Persistent settings** – stored in `~/.config/ortho_baa/config.json`.

## Install (dev)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ortho_baa.main
```

## Linux: add to Applications
```bash
chmod +x install_linux.sh
./install_linux.sh
```
- Icon → `~/.local/share/icons/ortho-baa.png`
- Launcher → `~/.local/bin/ortho-baa`
- Desktop entry → `~/.local/share/applications/ortho-baa.desktop`

Open your launcher and search **IPA Fixer – Before & After**.

## Usage
1. Drag **Before** and **After** images.
2. (Optional) enable **Crop** per image; tune top/bottom.
3. Choose **Output** folder, pick **PDF** or **JPEG**, click **Save** (or **Preview**).
4. Click **Go to folder** to open the output directory.

### Filename suggestions
- Parses names like `1234567_First_Last_composite.png` to suggest e.g.
  `1234567_First_Last_BeforeAndAfter.pdf`.
- Toggle the **Filename parts** checkboxes (**ID / First / Last**) to control output names.
- Preferences persist across runs.

## Troubleshooting
- **libpng error: IDAT: incorrect data check** – usually a corrupt input PNG; re-save/convert the image. The built-in icon is a clean PNG.
- **HEIC not loading** – ensure `pillow-heif` installed (it’s in `requirements.txt`).

## One-file builds (local)
```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --windowed --name OrthoBaA ortho_baa/main.py
```

## Linux AppImage (standalone)
Prereqs: `appimagetool` installed and on `PATH`.

```bash
./build_appimage.sh
```

Output AppImage will be created next to the `AppDir` inside `build/appimage/`.

## CI (GitHub Actions)
Tag to build and attach artifacts to Releases:
```bash
git tag v0.4.0
git push origin v0.4.0
```

## License
MIT
