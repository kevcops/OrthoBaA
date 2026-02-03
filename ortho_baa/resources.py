from __future__ import annotations

from pathlib import Path
import sys

ICON_FILENAME = "ipa-fixer-dark-512.png"

def _candidate_icon_paths() -> list[Path]:
    here = Path(__file__).resolve().parent
    candidates: list[Path] = []

    # 1) PyInstaller onefile/unpacked temp dir
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / "Icons" / ICON_FILENAME)

    # 2) Package-local assets (if we later vendor assets into the package)
    candidates.append(here / "assets" / "Icons" / ICON_FILENAME)

    # 3) Repo root assets (current layout)
    candidates.append(here.parent / "assets" / "Icons" / ICON_FILENAME)

    return candidates

def find_icon_path() -> Path | None:
    for p in _candidate_icon_paths():
        if p.exists():
            return p
    return None
