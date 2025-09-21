# IPA Fixer – Before & After PDF Tool

This is a simple **drag-and-drop desktop app** for creating printable *Before & After* comparison PDFs of orthodontic or dental images.  
Built with **PySide6**, **Pillow**, and **ReportLab**.

---

## ✨ Features
- Drag & drop one image into the **Before** pane, another into the **After** pane.
- Optional **per-image crop**:
  - Crop from the top, then finalize with a bottom-anchored height.
- Export to a **single-page, landscape PDF** (8.5" × 11").
- Images are scaled to **85% of their fit size** and centered.
- Default output directory:  
  `~/Documents/IPA Fixer/Before and After/`
- Suggested filename: `Before_vs_After.pdf` (editable).

---

## 📸 Screenshots
> _(Add screenshots here after you build the app)_  

---

## 🛠️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies
Make sure you have **Python 3.10+** installed. Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate

# Install required packages
python3 -m pip install --upgrade pip
python3 -m pip install PySide6 Pillow reportlab
```

On **Fedora/Linux**, you may also need Qt runtime libraries if you don’t already have them:

```bash
sudo dnf install -y qt6-qtbase-gui qt6-qtwayland   libxkbcommon-x11 xcb-util xcb-util-keysyms xcb-util-wm   xcb-util-image xcb-util-renderutil
```

---

## ▶️ Usage

Run the app from the project directory:

```bash
python3 OrthoBaA.py
```

- Drag your images into the Before/After panes.
- (Optional) check **Crop this image** and adjust Top/Bottom crop values.
- Choose your output folder and filename.
- Click **Save PDF**.

The resulting PDF will be ready in your chosen directory.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
