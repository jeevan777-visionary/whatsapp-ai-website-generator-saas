from __future__ import annotations

from utils.validators import validate_payload


def normalize_requirements(payload: dict) -> dict:
    payload = validate_payload(payload)
    payload.setdefault("required_sections", ["hero", "about", "services", "contact"])
    payload.setdefault("required_features", ["responsive", "seo"])
    return payload
