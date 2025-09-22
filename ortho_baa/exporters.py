
from __future__ import annotations
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .utils import fit_rect

LETTER_LANDSCAPE = landscape(letter)  # (792, 612)
MARGIN = 24
HALF_W = (LETTER_LANDSCAPE[0] - (MARGIN * 2)) / 2
DRAW_H = LETTER_LANDSCAPE[1] - (MARGIN * 2)

def export_pdf(out_path: Path, before: Image.Image, after: Image.Image, scale_factor: float = 0.85) -> Path:
    c = canvas.Canvas(str(out_path), pagesize=LETTER_LANDSCAPE)
    # Before
    bw, bh = before.size
    fit_bw, fit_bh = fit_rect(bw, bh, HALF_W, DRAW_H)
    fit_bw *= scale_factor
    fit_bh *= scale_factor
    bx = MARGIN + (HALF_W - fit_bw) / 2
    by = MARGIN + (DRAW_H - fit_bh) / 2
    # After
    aw, ah = after.size
    fit_aw, fit_ah = fit_rect(aw, ah, HALF_W, DRAW_H)
    fit_aw *= scale_factor
    fit_ah *= scale_factor
    ax = MARGIN + HALF_W + (HALF_W - fit_aw) / 2
    ay = MARGIN + (DRAW_H - fit_ah) / 2
    # Draw
    c.drawImage(ImageReader(before.convert("RGB")), bx, by, width=fit_bw, height=fit_bh, preserveAspectRatio=True)
    c.drawImage(ImageReader(after.convert("RGB")),  ax, ay, width=fit_aw, height=fit_ah, preserveAspectRatio=True)
    c.showPage()
    c.save()
    return out_path

def export_jpeg(out_path: Path, before: Image.Image, after: Image.Image, quality: int = 92, scale_factor: float = 0.85) -> Path:
    # 11x8.5in @300dpi -> 3300 x 2550 px
    target_w, target_h = (3300, 2550)
    margin = 90  # ~0.3"
    half_w = (target_w - (margin * 2)) // 2
    draw_h = target_h - (margin * 2)

    canvas_img = Image.new("RGB", (target_w, target_h), (255, 255, 255))

    def fit(w, h, bw, bh):
        fw, fh = fit_rect(w, h, bw, bh)
        return int(fw * scale_factor), int(fh * scale_factor)

    # Before
    bw, bh = before.size
    fw, fh = fit(bw, bh, half_w, draw_h)
    bx = margin + (half_w - fw) // 2
    by = margin + (draw_h - fh) // 2
    canvas_img.paste(before.convert("RGB").resize((fw, fh), Image.LANCZOS), (bx, by))

    # After
    aw, ah = after.size
    fw2, fh2 = fit(aw, ah, half_w, draw_h)
    ax = margin + half_w + (half_w - fw2) // 2
    ay = margin + (draw_h - fh2) // 2
    canvas_img.paste(after.convert("RGB").resize((fw2, fh2), Image.LANCZOS), (ax, ay))

    out_path = out_path.with_suffix(".jpg")
    canvas_img.save(out_path, "JPEG", quality=quality, optimize=True)
    return out_path
