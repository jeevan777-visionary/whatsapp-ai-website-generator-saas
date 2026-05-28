from __future__ import annotations

import json
from datetime import datetime

import database.db as db
from database.models import (
    AnalyticsEvent,
    DeploymentLog,
    DeploymentStatus,
    EditHistory,
    GeneratedWebsite,
    User,
    WebsiteRequest,
)


def _session():
    if db.SessionLocal is None:
        raise RuntimeError("Database not initialized")
    return db.SessionLocal()


def get_or_create_user(whatsapp_number: str, language: str = "en") -> User:
    db = _session()
    try:
        user = db.query(User).filter_by(whatsapp_number=whatsapp_number).first()
        if not user:
            user = User(whatsapp_number=whatsapp_number, language=language)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()


def get_user_by_email(email: str) -> User | None:
    db = _session()
    try:
        return db.query(User).filter_by(email=email).first()
    finally:
        db.close()


def create_user_by_email(email: str, password_hash: str, language: str = "en", role: str = "user") -> User:
    db = _session()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return existing
        # Legacy DB may have NOT NULL constraint on `whatsapp_number`, so we initialize it
        # with the email value until the user connects WhatsApp number in Settings.
        user = User(email=email, whatsapp_number=email, password_hash=password_hash, language=language, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def create_request(request_id: str, user_number: str, message: str) -> WebsiteRequest:
    db = _session()
    try:
        existing = db.query(WebsiteRequest).filter_by(request_id=request_id).first()
        if existing:
            existing.user_number = user_number
            existing.raw_message = message
            existing.status = "queued"
            existing.progress = existing.progress or 0
            db.commit()
            db.refresh(existing)
            return existing

        row = WebsiteRequest(
            request_id=request_id,
            user_number=user_number,
            raw_message=message,
            status="queued",
            progress=0,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    finally:
        db.close()


def update_request_status(
    request_id: str,
    status: str,
    progress: int = 0,
    live_url: str = "",
    extracted: dict | None = None,
    content: dict | None = None,
    website_type: str = "",
    site_slug: str = "",
) -> None:
    db = _session()
    try:
        row = db.query(WebsiteRequest).filter_by(request_id=request_id).first()
        if not row:
            return
        row.status = status
        row.progress = progress
        if live_url:
            row.live_url = live_url
        if extracted is not None:
            row.extracted_json = json.dumps(extracted)
        if content is not None:
            row.content_json = json.dumps(content)
        if website_type:
            row.website_type = website_type
        if site_slug:
            row.site_slug = site_slug
        row.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def upsert_deployment_status(request_id: str, phase: str, progress: int, message: str = "", live_url: str = "", error: str = "") -> None:
    db = _session()
    try:
        row = db.query(DeploymentStatus).filter_by(request_id=request_id).first()
        if not row:
            row = DeploymentStatus(request_id=request_id)
            db.add(row)
        row.phase = phase
        row.progress = progress
        row.message = message
        if live_url:
            row.live_url = live_url
        if error:
            row.error = error
        row.updated_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def save_generated_website(
    request_id: str,
    user_number: str,
    business_name: str,
    template_type: str,
    zip_path: str,
    preview_path: str,
    live_url: str = "",
    netlify_site_id: str = "",
) -> None:
    db = _session()
    try:
        row = db.query(GeneratedWebsite).filter_by(request_id=request_id).first()
        if not row:
            row = GeneratedWebsite(request_id=request_id, user_number=user_number)
            db.add(row)
        row.business_name = business_name
        row.template_type = template_type
        row.zip_path = zip_path
        row.preview_path = preview_path
        row.live_url = live_url
        row.netlify_site_id = netlify_site_id
        db.commit()
    finally:
        db.close()


def log_deployment(request_id: str, status: str, url: str = "", details: str = "", netlify_deploy_id: str = "") -> None:
    db = _session()
    try:
        db.add(
            DeploymentLog(
                request_id=request_id,
                status=status,
                url=url,
                details=details,
                netlify_deploy_id=netlify_deploy_id,
            )
        )
        db.commit()
    finally:
        db.close()


def log_edit(request_id: str, user_number: str, command: str, changes: dict) -> None:
    db = _session()
    try:
        db.add(
            EditHistory(
                request_id=request_id,
                user_number=user_number,
                command=command,
                changes_json=json.dumps(changes),
            )
        )
        db.commit()
    finally:
        db.close()


def track_event(event_type: str, request_id: str = "", user_number: str = "", metadata: dict | None = None) -> None:
    db = _session()
    try:
        db.add(
            AnalyticsEvent(
                event_type=event_type,
                request_id=request_id,
                user_number=user_number,
                metadata_json=json.dumps(metadata or {}),
            )
        )
        db.commit()
    finally:
        db.close()


def get_request(request_id: str) -> WebsiteRequest | None:
    db = _session()
    try:
        return db.query(WebsiteRequest).filter_by(request_id=request_id).first()
    finally:
        db.close()


def list_recent_requests(limit: int = 50) -> list[WebsiteRequest]:
    db = _session()
    try:
        return db.query(WebsiteRequest).order_by(WebsiteRequest.created_at.desc()).limit(limit).all()
    finally:
        db.close()


def list_requests_for_user_number(user_number: str, limit: int = 50) -> list[WebsiteRequest]:
    db = _session()
    try:
        return (
            db.query(WebsiteRequest)
            .filter_by(user_number=user_number)
            .order_by(WebsiteRequest.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def list_deployments_for_user_number(user_number: str, limit: int = 50) -> list[DeploymentLog]:
    db = _session()
    try:
        request_ids = [
            r.request_id
            for r in db.query(WebsiteRequest.request_id).filter_by(user_number=user_number).all()
        ]
        if not request_ids:
            return []
        return (
            db.query(DeploymentLog)
            .filter(DeploymentLog.request_id.in_(request_ids))
            .order_by(DeploymentLog.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def update_user_by_email(email: str, *, language: str | None = None, whatsapp_number: str | None = None) -> User | None:
    db = _session()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            return None
        if language:
            user.language = language
        if whatsapp_number is not None:
            user.whatsapp_number = whatsapp_number
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def analytics_summary() -> dict:
    db = _session()
    try:
        total = db.query(WebsiteRequest).count()
        completed = db.query(WebsiteRequest).filter_by(status="completed").count()
        failed = db.query(WebsiteRequest).filter_by(status="failed").count()
        deployed = db.query(GeneratedWebsite).filter(GeneratedWebsite.live_url != "").count()
        return {
            "total_requests": total,
            "completed": completed,
            "failed": failed,
            "deployed_sites": deployed,
            "success_rate": round((completed / total) * 100, 2) if total else 0,
        }
    finally:
        db.close()
