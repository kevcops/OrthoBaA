from __future__ import annotations
from pathlib import Path
from typing import Optional
from PIL import Image

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QPixmap, QImage, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QGroupBox, QLineEdit, QMessageBox, QFrame, QCheckBox, QSpinBox,
    QComboBox, QStatusBar, QProgressBar
)

from .utils import to_rgba
from .resources import find_icon_path

APP_STYLES = '''
*:focus { outline: none; }
QFrame { border: none; }
QFrame#dropPane { border: 2px dashed #888; border-radius: 12px; }
QLineEdit, QComboBox, QPushButton { border: 1px solid #bbb; border-radius: 6px; padding: 4px 8px; }
QPushButton:pressed { padding-top: 5px; padding-bottom: 3px; }
'''

def qpix_from_pil(img: Image.Image, max_w: int, max_h: int) -> QPixmap:
    im = to_rgba(img)
    w, h = im.size
    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
    im = im.resize((new_w, new_h), Image.LANCZOS)
    data = im.tobytes("raw", "RGBA")
    qimg = QImage(data, im.size[0], im.size[1], QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)

class DropPane(QFrame):
    pathChanged = Signal(str)
    imageChanged = Signal()

    def __init__(self, title: str, default_top: int = 3250, default_bottom: int = 3020):
        super().__init__()
        self.setObjectName("dropPane")
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)

        self._path: Optional[Path] = None
        self._pil: Optional[Image.Image] = None

        self.title = QLabel(title); self.title.setAlignment(Qt.AlignCenter); self.title.setStyleSheet("font-weight:600;")
        self.thumb = QLabel("Drop image here"); self.thumb.setAlignment(Qt.AlignCenter); self.thumb.setMinimumHeight(220)

        self.crop_check = QCheckBox("Crop this image")
        self.top_spin = QSpinBox(); self.top_spin.setRange(1, 100000); self.top_spin.setValue(default_top)
        self.bottom_spin = QSpinBox(); self.bottom_spin.setRange(1, 100000); self.bottom_spin.setValue(default_bottom)

        crop_row = QHBoxLayout()
        crop_row.addWidget(self.crop_check); crop_row.addSpacing(12)
        crop_row.addWidget(QLabel("Top:")); crop_row.addWidget(self.top_spin)
        crop_row.addSpacing(12); crop_row.addWidget(QLabel("Bottom:")); crop_row.addWidget(self.bottom_spin)
        crop_row.addStretch(1)

        self.choose_btn = QPushButton("Choose…"); self.clear_btn  = QPushButton("Clear")
        btn_row = QHBoxLayout(); btn_row.addWidget(self.choose_btn); btn_row.addWidget(self.clear_btn)

        lay = QVBoxLayout(self)
        lay.addWidget(self.title); lay.addWidget(self.thumb, 1); lay.addLayout(crop_row); lay.addLayout(btn_row)

        self.choose_btn.clicked.connect(self.choose_file)
        self.clear_btn.clicked.connect(self.clear)
        self.crop_check.toggled.connect(self._update_crop_state)
        self.top_spin.valueChanged.connect(self._refresh_preview)
        self.bottom_spin.valueChanged.connect(self._refresh_preview)
        self._update_crop_state()

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @property
    def pil_image(self) -> Optional[Image.Image]:
        return self._pil

    def choose_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Select image", str(Path.home()),
                                           "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp *.heic *.heif *.avif)")
        if p:
            self.set_path(Path(p))

    def clear(self):
        self._path = None; self._pil = None
        self.thumb.setText("Drop image here")
        self.pathChanged.emit(""); self.imageChanged.emit()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if not urls: return
        for u in urls:
            p = Path(u.toLocalFile())
            if p.exists() and p.is_file():
                self.set_path(p); break

    def set_path(self, p: Path):
        from .logic import load_image
        im = load_image(p)
        if im is None:
            QMessageBox.warning(self, "Invalid image", f"Could not load:\n{p}")
            return
        self._path = p; self._pil = im
        self._refresh_preview()
        self.pathChanged.emit(str(p)); self.imageChanged.emit()

    def get_effective_image(self) -> Optional[Image.Image]:
        from .logic import crop_top_then_bottom, CropParams
        if self._pil is None: return None
        if self.crop_check.isChecked():
            return crop_top_then_bottom(self._pil, CropParams(True, self.top_spin.value(), self.bottom_spin.value()))
        return self._pil

    def _refresh_preview(self):
        eff = self.get_effective_image()
        if eff is None: self.thumb.setText("Drop image here")
        else: self.thumb.setPixmap(qpix_from_pil(eff, 520, 360))
        self.imageChanged.emit()

    def _update_crop_state(self):
        enabled = self.crop_check.isChecked()
        self.top_spin.setEnabled(enabled); self.bottom_spin.setEnabled(enabled)
        self._refresh_preview()

def make_window_icon() -> QIcon:
    try:
        p = find_icon_path()
        if not p:
            return QIcon()
        return QIcon(str(p))
    except Exception:
        return QIcon()

class MainWindow(QMainWindow):
    saveRequested = Signal()
    previewRequested = Signal()
    batchRequested = Signal()

    def __init__(self, out_dir_default: Path, output_format_default: str = "PDF"):
        super().__init__()
        self.setWindowTitle("Ortho Before and After")
        self.setWindowIcon(make_window_icon())
        self.resize(1080, 660)

        # Apply global app stylesheet for clean look
        self.setStyleSheet(APP_STYLES)

        self.before = DropPane("Before")
        self.after  = DropPane("After")

        out_group = QGroupBox("Output")
        self.out_dir = QLineEdit(str(out_dir_default))
        self.choose_out = QPushButton("Choose…"); self.choose_out.clicked.connect(self._choose_out_dir)
        self.filename = QLineEdit(""); self.filename.setPlaceholderText("Output filename (e.g., Patient_BeforeAndAfter.pdf)")
        self.format_combo = QComboBox(); self.format_combo.addItems(["PDF", "JPEG"]); self.format_combo.setCurrentText(output_format_default)
        self.save_btn = QPushButton("Save"); self.preview_btn = QPushButton("Preview")

        r1 = QHBoxLayout(); r1.addWidget(QLabel("Output folder:")); r1.addWidget(self.out_dir, 1); r1.addWidget(self.choose_out)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Filename:")); r2.addWidget(self.filename, 1); r2.addWidget(QLabel("Format:")); r2.addWidget(self.format_combo); r2.addWidget(self.preview_btn); r2.addWidget(self.save_btn)

        parts_group = QGroupBox("Filename parts")
        self.name_id_cb = QCheckBox("ID"); self.name_first_cb = QCheckBox("First"); self.name_last_cb = QCheckBox("Last")
        parts_row = QHBoxLayout(parts_group); parts_row.addWidget(self.name_id_cb); parts_row.addWidget(self.name_first_cb); parts_row.addWidget(self.name_last_cb); parts_row.addStretch(1)

        out_lay = QVBoxLayout(out_group); out_lay.addLayout(r1); out_lay.addLayout(r2); out_lay.addWidget(parts_group)

        batch_row = QHBoxLayout(); self.batch_btn = QPushButton("Batch: Choose folder…"); batch_row.addStretch(1); batch_row.addWidget(self.batch_btn)

        panes = QHBoxLayout(); panes.addWidget(self.before, 1); panes.addWidget(self.after, 1)
        central = QWidget(); main = QVBoxLayout(central); main.addLayout(panes, 1); main.addWidget(out_group); main.addLayout(batch_row)
        self.setCentralWidget(central)

        self.status = QStatusBar(); self.setStatusBar(self.status)
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0); self.progress.setFixedWidth(200)
        self.status.addPermanentWidget(self.progress)

        self.open_folder_btn = QPushButton("Go to folder"); self.open_folder_btn.setEnabled(False)
        self.status.addPermanentWidget(self.open_folder_btn)
        self.open_folder_btn.clicked.connect(self._open_folder)

        self.save_btn.clicked.connect(self.saveRequested.emit)
        self.preview_btn.clicked.connect(self.previewRequested.emit)
        self.batch_btn.clicked.connect(self.batchRequested.emit)

    def _choose_out_dir(self):
        p = QFileDialog.getExistingDirectory(self, "Select output folder", self.out_dir.text().strip() or str(Path.home()))
        if p: self.out_dir.setText(p)

    def _open_folder(self):
        out_dir = Path(self.out_dir.text().strip())
        if out_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(out_dir)))
