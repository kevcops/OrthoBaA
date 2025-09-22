
from __future__ import annotations
import sys, webbrowser
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from .ui import MainWindow
from .config import load_config, save_config
from .logic import load_image, CropParams, crop_top_then_bottom, guess_pairs_in_folder
from .exporters import export_pdf, export_jpeg

def open_file(path: Path) -> None:
    try:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
    except Exception:
        try:
            webbrowser.open(str(path))
        except Exception:
            pass

def run_app():
    cfg = load_config()
    app = QApplication(sys.argv)
    win = MainWindow(out_dir_default=Path(cfg["last_out_dir"]), output_format_default=cfg.get("output_format","PDF"))

    def suggest_name():
        if win.filename.text().strip():
            return
        b = Path(win.before.path).stem if win.before.path else "Before"
        a = Path(win.after.path).stem if win.after.path else "After"
        ext = ".pdf" if win.format_combo.currentText() == "PDF" else ".jpg"
        win.filename.setText(f"{b}_vs_{a}{ext}")

    win.before.pathChanged.connect(lambda _: suggest_name())
    win.after.pathChanged.connect(lambda _: suggest_name())

    def get_effective_images():
        b_img = win.before.get_effective_image()
        a_img = win.after.get_effective_image()
        if b_img is None or a_img is None:
            QMessageBox.warning(win, "Missing images", "Please add both Before and After images.")
            return None, None
        return b_img, a_img

    def do_export(preview: bool = False):
        out_dir = Path(win.out_dir.text().strip() or cfg["last_out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = win.format_combo.currentText()
        name = win.filename.text().strip()
        if not name:
            b = Path(win.before.path).stem if win.before.path else "Before"
            a = Path(win.after.path).stem if win.after.path else "After"
            name = f"{b}_vs_{a}"
        out_path = out_dir / name
        if fmt == "PDF" and not out_path.suffix.lower().endswith(".pdf"):
            out_path = out_path.with_suffix(".pdf")
        if fmt == "JPEG" and not out_path.suffix.lower().endswith(".jpg"):
            out_path = out_path.with_suffix(".jpg")

        b_img, a_img = get_effective_images()
        if b_img is None:
            return

        win.status.showMessage("Exporting…"); win.progress.setValue(10); app.processEvents()

        scale = float(cfg.get("scale_factor", 0.85))
        if fmt == "PDF":
            out_file = export_pdf(out_path, b_img, a_img, scale_factor=scale)
        else:
            out_file = export_jpeg(out_path, b_img, a_img, quality=92, scale_factor=scale)

        win.progress.setValue(100); win.status.showMessage(f"Saved to: {out_file}")
        if preview:
            QTimer.singleShot(50, lambda: open_file(out_file))

        cfg["last_out_dir"] = str(out_dir); cfg["output_format"] = fmt; save_config(cfg)

    def do_batch():
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(win, "Choose folder containing pairs", str(Path.home()))
        if not folder:
            return
        folder = Path(folder)
        pairs = guess_pairs_in_folder(folder)
        if not pairs:
            QMessageBox.information(win, "Nothing found", "No pairs detected in that folder.")
            return

        out_dir = Path(win.out_dir.text().strip() or cfg["last_out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = win.format_combo.currentText()
        scale = float(cfg.get("scale_factor", 0.85))

        win.progress.setValue(0); win.status.showMessage(f"Batch: processing {len(pairs)} pair(s)…"); app.processEvents()

        for i, (b_path, a_path, stem) in enumerate(pairs, start=1):
            b = load_image(b_path); a = load_image(a_path)
            if not b or not a:
                continue
            b_params = CropParams(win.before.crop_check.isChecked(), win.before.top_spin.value(), win.before.bottom_spin.value())
            a_params = CropParams(win.after.crop_check.isChecked(),  win.after.top_spin.value(),  win.after.bottom_spin.value())
            b_eff = crop_top_then_bottom(b, b_params); a_eff = crop_top_then_bottom(a, a_params)

            out_path = out_dir / f"{stem}_BeforeAndAfter"
            if fmt == "PDF":
                export_pdf(out_path.with_suffix(".pdf"), b_eff, a_eff, scale_factor=scale)
            else:
                export_jpeg(out_path.with_suffix(".jpg"), b_eff, a_eff, quality=92, scale_factor=scale)

            win.progress.setValue(int(i / len(pairs) * 100)); app.processEvents()

        win.status.showMessage("Batch complete."); cfg["last_out_dir"] = str(out_dir); cfg["output_format"] = fmt; save_config(cfg)

    win.saveRequested.connect(lambda: do_export(preview=False))
    win.previewRequested.connect(lambda: do_export(preview=True))
    win.batchRequested.connect(do_batch)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
