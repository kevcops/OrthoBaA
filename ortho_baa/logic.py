from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from PIL import Image, UnidentifiedImageError

# Enable HEIC/HEIF/AVIF if pillow-heif is installed
try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".heic", ".heif", ".avif"}

@dataclass
class CropParams:
    enabled: bool
    top: int
    bottom: int

def load_image(p: Path) -> Optional[Image.Image]:
    if not p.exists() or not p.is_file():
        return None
    if p.suffix.lower() not in SUPPORTED_EXTS:
        return None
    try:
        im = Image.open(p)
        im.load()  # force read; avoids lazy decoding errors later
        return im
    except (UnidentifiedImageError, OSError):
        return None

def crop_top_then_bottom(img: Image.Image, params: CropParams) -> Image.Image:
    if not params.enabled:
        return img
    w, h = img.size
    # Keep top N rows
    stage1 = img.crop((0, 0, w, min(params.top, h)))
    h1 = stage1.height
    # Then keep bottom M rows from that
    if h1 > params.bottom:
        return stage1.crop((0, h1 - params.bottom, w, h1))
    return stage1

def guess_pairs_in_folder(folder: Path) -> List[Tuple[Path, Path, str]]:
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]
    files.sort(key=lambda x: x.name.lower())
    pairs: List[Tuple[Path, Path, str]] = []

    by_stem: Dict[str, Dict[str, Path]] = {}
    for f in files:
        stem = f.stem.lower()
        if stem.endswith((" before", "-before", "_before")):
            key = stem.rsplit("before", 1)[0].rstrip(" -_")
            by_stem.setdefault(key, {})["before"] = f
        elif stem.endswith((" after", "-after", "_after")):
            key = stem.rsplit("after", 1)[0].rstrip(" -_")
            by_stem.setdefault(key, {})["after"] = f

    for k, v in list(by_stem.items()):
        if "before" in v and "after" in v:
            base = k.strip() or "Pair"
            pairs.append((v["before"], v["after"], base))

    used = set([p for trio in pairs for p in (trio[0], trio[1])])
    remaining = [f for f in files if f not in used]

    for i in range(0, len(remaining), 2):
        if i + 1 < len(remaining):
            b, a = remaining[i], remaining[i + 1]
            base = b.stem
            pairs.append((b, a, base))

    return pairs
