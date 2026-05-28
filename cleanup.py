from __future__ import annotations

import shutil
from pathlib import Path


def cleanup_artifacts(site_dir: Path, zip_path: Path) -> None:
    if site_dir.exists():
        shutil.rmtree(site_dir, ignore_errors=True)
    if zip_path.exists():
        zip_path.unlink(missing_ok=True)
