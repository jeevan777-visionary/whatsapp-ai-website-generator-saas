from __future__ import annotations

import re
from typing import Any

from utils.constants import SUPPORTED_WEBSITE_TYPES


def sanitize_text(text: str) -> str:
    return re.sub(r"[^\w\s@+.,:/#&-]", "", text).strip()


def validate_website_type(value: str) -> str:
    normalized = value.lower().strip()
    return normalized if normalized in SUPPORTED_WEBSITE_TYPES else "agency"


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    payload["website_type"] = validate_website_type(str(payload.get("website_type", "agency")))
    payload["business_name"] = sanitize_text(str(payload.get("business_name", "Your Brand")))[:80]
    return payload
