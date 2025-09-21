#!/usr/bin/env python3
# OrthoBaA.py
#
# Drag-and-drop Qt app to create a 1-page, landscape 8.5"x11" PDF (Before on left, After on right).
# Dependencies: PySide6, Pillow, reportlab
#   python3 -m pip install --upgrade PySide6 Pillow reportlab
#
# If no window appears:
#   - Try: QT_QPA_PLATFORM=wayland python3 OrthoBaA.py
#   - Or : QT_QPA_PLATFORM=xcb     python3 OrthoBaA.py
#   - On Fedora, install Qt GUI bits:
#       sudo dnf install -y qt6-qtbase-gui qt6-qtwayland \
#           libxkbcommon-x11 xcb-util xcb-util-keysyms xcb-util-wm xcb-util-image xcb-util-renderutil

import os
import sys
from pathlib import Path
from typing import Optional

# Prefer Wayland; can be overridden at launch
os.environ.setdefault("QT_QPA_PLATFORM", "wayland")

print("[OrthoBaA] starting…", flush=True)
print(f"[OrthoBaA] QT_QPA_PLATFORM={os.environ.get('QT_QPA_PLATFORM')}", flush=True)

from PIL import Image
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from PySide6.QtCore import Qt, Signal, QTimer, QRect
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QGroupBox, QLineEdit, QMessageBox, QFrame
)

PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)  # (792, 612 points at 72dpi)
MARGIN = 24
HALF_WIDTH = (PAGE_WIDTH - (MARGIN * 2)) / 2
DRAW_HEIGHT = PAGE_HEIGHT - (MARGIN * 2)

DEFAULT_OUTDIR = Path.home() / "Documents" / "IPA Fixer" / "Before and After"
SCALE_FACTOR = 0.85   # images drawn at 85% of their fitted size


def pil_to_qpixmap(img: Image.Image, max_w: int, max_h: int) -> QPixmap:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    w, h = img.size
    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.size[0], img.size[1], QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


def fit_rect(w: float, h: float, box_w: float, box_h: float) -> tuple[float, float]:
    if w <= 0 or h <= 0:
        return (box_w, box_h)
    scale = min(box_w / w, box_h / h)
    return (w * scale, h * scale)


class DropPane(QFrame):
    pathChanged = Signal(str)

    def __init__(self, title: str):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame { border:2px dashed #888; border-radius:12px; }")

        # Type-annotated state
        self._path: Optional[Path] = None
        self._pil_image: Optional[Image.Image] = None

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-weight:600;")

        self.thumb = QLabel("Drop image here")
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setMinimumHeight(220)

        self.load_btn = QPushButton("Choose…")
        self.clear_btn = QPushButton("Clear")

        lay = QVBoxLayout(self)
        lay.addWidget(self.title)
        lay.addWidget(self.thumb, 1)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.clear_btn)
        lay.addLayout(btn_row)

        self.load_btn.clicked.connect(self.choose_file)
        self.clear_btn.clicked.connect(self.clear)

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @property
    def pil_image(self) -> Optional[Image.Image]:
        return self._pil_image

    def choose_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select image", str(Path.home()),
                                           "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        if p:
            self.set_path(Path(p))

    def clear(self):
        self._path = None
        self._pil_image = None
        self.thumb.setText("Drop image here")
        self.pathChanged.emit("")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        for u in urls:
            p = Path(u.toLocalFile())
            if p.exists() and p.is_file():
                self.set_path(p)
                break

    def set_path(self, p: Path):
        try:
            im = Image.open(p)
            im.load()
            self._path = p
            self._pil_image = im.convert("RGBA")
            pix = pil_to_qpixmap(self._pil_image, 520, 360)
            self.thumb.setPixmap(pix)
            self.pathChanged.emit(str(p))
        except Exception as e:
            QMessageBox.warning(self, "Invalid image", f"Could not load image:\n{e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("[OrthoBaA] building UI…", flush=True)
        self.setWindowTitle("IPA Fixer – Before & After")
        self.resize(1000, 600)

        DEFAULT_OUTDIR.mkdir(parents=True, exist_ok=True)

        self.before_pane = DropPane("Before")
        self.after_pane  = DropPane("After")

        out_group = QGroupBox("Output")
        self.out_dir_edit = QLineEdit(str(DEFAULT_OUTDIR))
        self.out_browse = QPushButton("Choose folder…")
        self.out_browse.clicked.connect(self.choose_out_dir)
        self.filename_edit = QLineEdit("")
        self.filename_edit.setPlaceholderText("Output filename (e.g., Smith_BeforeAndAfter.pdf)")
        self.save_btn = QPushButton("Save PDF")
        self.save_btn.clicked.connect(self.save_pdf)

        out_row1 = QHBoxLayout()
        out_row1.addWidget(QLabel("Output folder:"))
        out_row1.addWidget(self.out_dir_edit, 1)
        out_row1.addWidget(self.out_browse)

        out_row2 = QHBoxLayout()
        out_row2.addWidget(QLabel("Filename:"))
        out_row2.addWidget(self.filename_edit, 1)
        out_row2.addWidget(self.save_btn)

        out_lay = QVBoxLayout(out_group)
        out_lay.addLayout(out_row1)
        out_lay.addLayout(out_row2)

        panes = QHBoxLayout()
        panes.addWidget(self.before_pane, 1)
        panes.addWidget(self.after_pane, 1)

        central = QWidget()
        main = QVBoxLayout(central)
        main.addLayout(panes, 1)
        main.addWidget(out_group)
        self.setCentralWidget(central)

        # Suggest name when both panes have images
        self.before_pane.pathChanged.connect(self._maybe_suggest_name)
        self.after_pane.pathChanged.connect(self._maybe_suggest_name)

        # Bring window to front & center after it shows
        QTimer.singleShot(0, self._focus_and_center)

    def _focus_and_center(self):
        try:
            screen = self.screen() or QApplication.primaryScreen()
            if screen:
                geo: QRect = screen.availableGeometry()
                self.move(geo.center().x() - self.width() // 2,
                          geo.center().y() - self.height() // 2)
        except Exception:
            pass
        self.raise_()
        self.activateWindow()
        print("[OrthoBaA] UI shown (should be visible now).", flush=True)

    def choose_out_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select output folder", str(DEFAULT_OUTDIR))
        if d:
            self.out_dir_edit.setText(d)

    def _maybe_suggest_name(self, _=None):
        if self.filename_edit.text().strip():
            return
        b = self.before_pane.path
        a = self.after_pane.path
        if b and a:
            self.filename_edit.setText(f"{b.stem}_vs_{a.stem}.pdf")

    def save_pdf(self):
        if self.before_pane.pil_image is None or self.after_pane.pil_image is None:
            QMessageBox.warning(self, "Missing images", "Please add both Before and After images.")
            return

        out_dir = Path(self.out_dir_edit.text().strip()) if self.out_dir_edit.text().strip() else DEFAULT_OUTDIR
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = self.filename_edit.text().strip()
        if not filename:
            b = self.before_pane.path.stem if self.before_pane.path else "Before"
            a = self.after_pane.path.stem if self.after_pane.path else "After"
            filename = f"{b}_vs_{a}.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        out_path = out_dir / filename

        try:
            self._render_pdf(out_path, self.before_pane.pil_image, self.after_pane.pil_image)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{e}")
            return

        QMessageBox.information(self, "Saved", f"PDF saved to:\n{out_path}")

    def _render_pdf(self, out_path: Path, before_img: Image.Image, after_img: Image.Image):
        c = canvas.Canvas(str(out_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

        # Before image
        bw, bh = before_img.size
        fit_bw, fit_bh = fit_rect(bw, bh, HALF_WIDTH, DRAW_HEIGHT)
        fit_bw *= SCALE_FACTOR
        fit_bh *= SCALE_FACTOR
        bx = MARGIN + (HALF_WIDTH - fit_bw) / 2
        by = MARGIN + (DRAW_HEIGHT - fit_bh) / 2

        # After image
        aw, ah = after_img.size
        fit_aw, fit_ah = fit_rect(aw, ah, HALF_WIDTH, DRAW_HEIGHT)
        fit_aw *= SCALE_FACTOR
        fit_ah *= SCALE_FACTOR
        ax = MARGIN + HALF_WIDTH + (HALF_WIDTH - fit_aw) / 2
        ay = MARGIN + (DRAW_HEIGHT - fit_ah) / 2

        c.drawImage(ImageReader(before_img.convert("RGB")), bx, by,
                    width=fit_bw, height=fit_bh, preserveAspectRatio=True)
        c.drawImage(ImageReader(after_img.convert("RGB")), ax, ay,
                    width=fit_aw, height=fit_ah, preserveAspectRatio=True)

        c.showPage()
        c.save()


def main():
    print("[OrthoBaA] creating QApplication…", flush=True)
    app = QApplication(sys.argv)
    print("[OrthoBaA] QApplication created. Launching window…", flush=True)
    win = MainWindow()
    win.show()
    print("[OrthoBaA] entering event loop…", flush=True)
    rc = app.exec()
    print(f"[OrthoBaA] event loop exited with rc={rc}", flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("\n[OrthoBaA] FATAL:", repr(e), flush=True)
        traceback.print_exc()
        raise
