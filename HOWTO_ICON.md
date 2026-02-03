
# HOWTO: Update App Icons

The app now loads icons directly from `assets/Icons/ipa-fixer-dark-512.png`.

## 1) Replace the app icon
- Swap the PNG at: `assets/Icons/ipa-fixer-dark-512.png`.
- (Optional) Update other sizes in `assets/Icons/` for launchers or tray use.

## 2) Linux desktop entry
Re-run the installer to copy the icon into your user icon theme:
```bash
chmod +x install_linux.sh
./install_linux.sh
```

## 3) Standalone builds
The build scripts now include the icon file automatically:
- Linux AppImage: `./build_appimage.sh`
- Windows: `build_win.bat`
- macOS: `build_mac.sh`
