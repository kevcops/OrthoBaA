from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path.home() / ".config" / "ortho_baa"
APP_DIR.mkdir(parents=True, exist_ok=True)
CFG_PATH = APP_DIR / "config.json"

DEFAULTS: Dict[str, Any] = {
    "last_out_dir": str((Path.home() / "Documents" / "IPA Fixer" / "Before and After")),
    "scale_factor": 0.85,
    "crop_defaults": {"top": 3250, "bottom": 3020},
    "output_format": "PDF",
    "name_parts": {"use_id": True, "use_first": True, "use_last": True},
}

def load_config() -> Dict[str, Any]:
    if CFG_PATH.exists():
        try:
            data = json.loads(CFG_PATH.read_text())
            cfg = {**DEFAULTS, **data}
            np = cfg.get("name_parts") or {}
            cfg["name_parts"] = {
                "use_id": bool(np.get("use_id", True)),
                "use_first": bool(np.get("use_first", True)),
                "use_last": bool(np.get("use_last", True)),
            }
            return cfg
        except Exception:
            pass
    return DEFAULTS.copy()

def save_config(cfg: Dict[str, Any]) -> None:
    try:
        CFG_PATH.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass
