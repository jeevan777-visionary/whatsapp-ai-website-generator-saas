from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


def generate_request_id() -> str:
    return str(uuid.uuid4())


def safe_json_loads(value: str) -> dict[str, Any]:
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
