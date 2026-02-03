from __future__ import annotations
from pathlib import Path
from typing import Tuple
from PIL import Image
import re

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

# ---------------- Filename parsing & name suggestion ----------------

_PAT = re.compile(
    r"""
    ^\s*
    (?P<id>\d+)                # numeric patient id at start
    [_\-\s]+
    (?P<first>[A-Za-z]+)        # first name (letters)
    [_\-\s]+
    (?P<last>[A-Za-z][A-Za-z\-']*)  # last name (letters, hyphen/apostrophe)
    (?:[_\-\s]+(?P<trailing>.*?))?  # optional trailing descriptor
    (?:\(\d+\))?              # optional copy suffix like (1)
    \.[A-Za-z0-9]+              # extension
    \s*$
    """, re.VERBOSE,
)

def _cap(s: str) -> str:
    # Preserve hyphens/apostrophes while Title-casing parts
    parts = re.split(r"([\-'])", s)
    return "".join(p.capitalize() if p.isalpha() else p for p in parts)

def parse_patient_from_filename(filename: str):
    name = Path(filename).name
    m = _PAT.match(name)
    if not m:
        return None
    pid = m.group("id")
    first = _cap(m.group("first"))
    last = _cap(m.group("last"))
    return {"id": pid, "first": first, "last": last}

def _compose_from_info(info: dict, use_id: bool, use_first: bool, use_last: bool) -> str:
    parts = []
    if use_id:
        parts.append(info["id"])
    if use_first:
        parts.append(info["first"])
    if use_last:
        parts.append(info["last"])
    if not parts:
        parts = [info.get("id") or info.get("first") or info.get("last") or "Patient"]
    return "_".join([p for p in parts if p])

def suggest_output_basename_from_two_with_prefs(before_name: str, after_name: str, use_id: bool, use_first: bool, use_last: bool) -> str:
    b = parse_patient_from_filename(before_name) if before_name else None
    a = parse_patient_from_filename(after_name) if after_name else None
    info = None
    if b and a:
        if b["id"] == a["id"] or (b["first"] == a["first"] and b["last"] == a["last"]):
            info = b
        else:
            info = b  # prefer before deterministically
    elif b:
        info = b
    elif a:
        info = a
    if info:
        return f"{_compose_from_info(info, use_id, use_first, use_last)}_BeforeAndAfter"
    return "Before_vs_After"
