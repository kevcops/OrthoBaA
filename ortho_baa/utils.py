
from __future__ import annotations
from pathlib import Path
from typing import Tuple
from PIL import Image

def fit_rect(w: float, h: float, box_w: float, box_h: float) -> Tuple[float, float]:
    if w <= 0 or h <= 0:
        return (box_w, box_h)
    s = min(box_w / w, box_h / h)
    return (w * s, h * s)

def to_rgba(img: Image.Image) -> Image.Image:
    return img if img.mode in ("RGB", "RGBA") else img.convert("RGBA")

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p
