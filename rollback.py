from __future__ import annotations

import os

import requests

from utils.logger import get_logger

logger = get_logger(__name__)
NETLIFY_API = "https://api.netlify.com/api/v1"


def rollback_deployment(site_id: str, deploy_id: str) -> bool:
    token = os.getenv("NETLIFY_AUTH_TOKEN", "")
    if not token or not site_id or not deploy_id:
        logger.warning("Rollback skipped: missing credentials or IDs.")
        return False

    response = requests.post(
        f"{NETLIFY_API}/sites/{site_id}/deploys/{deploy_id}/restore",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if response.status_code >= 400:
        logger.error("Rollback failed: %s", response.text)
        return False
    return True
