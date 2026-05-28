from __future__ import annotations

from pathlib import Path

from deployment.netlify import deploy_zip_to_netlify, slugify_site_name, validate_live_url
from deployment.retry import with_retry
from utils.logger import get_logger

logger = get_logger(__name__)


def deploy_site(zip_path: Path, request_id: str, business_name: str = "website") -> dict:
    site_name = slugify_site_name(business_name, suffix=request_id.replace("-", "")[:6])
    live_url, site_id, deploy_id = with_retry(
        lambda: deploy_zip_to_netlify(zip_path, site_name),
        attempts=3,
        delay=2.0,
    )
    if not validate_live_url(live_url):
        logger.warning("Live URL validation failed for %s", live_url)

    return {
        "live_url": live_url,
        "site_id": site_id,
        "deploy_id": deploy_id,
        "site_slug": site_name,
    }
