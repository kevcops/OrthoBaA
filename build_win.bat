
@echo off
REM Build Windows EXE with PyInstaller
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --onefile --windowed --name OrthoBaA -p . ortho_baa\main.py
echo Done. See dist\OrthoBaA.exe
