from __future__ import annotations

import os

import requests

from utils.logger import get_logger

logger = get_logger(__name__)
NETLIFY_API = "https://api.netlify.com/api/v1"


def map_custom_domain(site_id: str, domain: str) -> bool:
    token = os.getenv("NETLIFY_AUTH_TOKEN", "")
    if not token or not site_id:
        logger.warning("Custom domain mapping skipped.")
        return False

    response = requests.post(
        f"{NETLIFY_API}/sites/{site_id}/domains",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"domain": domain},
        timeout=30,
    )
    if response.status_code >= 400:
        logger.error("Domain mapping failed: %s", response.text)
        return False
    return True
