from __future__ import annotations

import os
import re
import time
from pathlib import Path

import requests

from utils.constants import REQUEST_TIMEOUT_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)
NETLIFY_API = "https://api.netlify.com/api/v1"


def slugify_site_name(name: str, suffix: str = "") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = slug[:40] or "wa-site"
    if suffix:
        slug = f"{slug}-{suffix[:6]}"
    return slug


def _headers() -> dict:
    token = os.getenv("NETLIFY_AUTH_TOKEN", "")
    return {"Authorization": f"Bearer {token}"}


def create_site(site_name: str) -> dict:
    response = requests.post(
        f"{NETLIFY_API}/sites",
        headers={**_headers(), "Content-Type": "application/json"},
        json={"name": site_name},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def deploy_zip(site_id: str, zip_path: Path) -> dict:
    with zip_path.open("rb") as handle:
        response = requests.post(
            f"{NETLIFY_API}/sites/{site_id}/deploys",
            headers={**_headers(), "Content-Type": "application/zip"},
            data=handle.read(),
            timeout=120,
        )
    response.raise_for_status()
    return response.json()


def wait_for_deploy(site_id: str, deploy_id: str, attempts: int = 20, delay: float = 3.0) -> dict:
    for _ in range(attempts):
        response = requests.get(
            f"{NETLIFY_API}/sites/{site_id}/deploys/{deploy_id}",
            headers=_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        state = payload.get("state", "")
        if state == "ready":
            return payload
        if state in {"error", "failed"}:
            raise RuntimeError(f"Netlify deploy failed: {payload}")
        time.sleep(delay)
    raise TimeoutError("Netlify deploy timed out")


def deploy_zip_to_netlify(zip_path: Path, site_name: str) -> tuple[str, str, str]:
    """Deploy zip and return (live_url, site_id, deploy_id)."""
    token = os.getenv("NETLIFY_AUTH_TOKEN", "")
    if not token:
        fallback = f"https://{site_name}.netlify.app"
        logger.warning("NETLIFY_AUTH_TOKEN missing; returning predictable fallback URL.")
        return fallback, "", ""

    site = create_site(site_name)
    site_id = site["id"]
    deploy = deploy_zip(site_id, zip_path)
    deploy_id = deploy["id"]
    ready = wait_for_deploy(site_id, deploy_id)

    live_url = (
        ready.get("ssl_url")
        or ready.get("deploy_ssl_url")
        or site.get("ssl_url")
        or site.get("url")
        or f"https://{site_name}.netlify.app"
    )
    logger.info("Deployed site %s -> %s", site_name, live_url)
    return live_url, site_id, deploy_id


def validate_live_url(url: str) -> bool:
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        return response.status_code < 500
    except requests.RequestException:
        return False
