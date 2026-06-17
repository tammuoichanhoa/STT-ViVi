from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "STT_Vi"


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return resource_root()


def user_data_root() -> Path:
    if getattr(sys, "frozen", False) and os.name == "nt":
        base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base_dir / APP_NAME
    return application_root()


def ensure_runtime_dirs() -> dict[str, Path]:
    root = user_data_root()
    upload_dir = root / "uploads"
    output_dir = root / "outputs"

    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return {
        "root": root,
        "upload_dir": upload_dir,
        "output_dir": output_dir,
    }
