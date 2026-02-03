
@echo off
REM Build Windows EXE with PyInstaller
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --onefile --windowed --name OrthoBaA -p . --add-data "assets\\Icons\\ipa-fixer-dark-512.png;assets\\Icons" app.py
echo Done. See dist\OrthoBaA.exe
