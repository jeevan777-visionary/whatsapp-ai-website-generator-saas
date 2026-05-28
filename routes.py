from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request, send_file

from database.db import SessionLocal
from database.repository import (
    create_request,
    create_user_by_email,
    get_or_create_user,
    get_request,
    get_user_by_email,
    list_requests_for_user_number,
    list_deployments_for_user_number,
    update_user_by_email,
)
from middleware.auth import require_auth
from tasks.celery_worker import should_run_sync
from tasks.generation_tasks import enqueue_website_request
from utils.auth import create_access_token, hash_password, verify_password
from utils.helpers import generate_request_id

api_bp = Blueprint("api", __name__, url_prefix="/api")


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@api_bp.post("/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 chars"}), 400

    if get_user_by_email(email):
        return jsonify({"error": "Email already in use"}), 409

    password_hash = hash_password(password)
    user = create_user_by_email(email=email, password_hash=password_hash, role="user")
    token = create_access_token(user_id=user.id, email=user.email or email, role=user.role)
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}})


@api_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    user = get_user_by_email(email)
    if not user or not user.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401
    if not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(user_id=user.id, email=user.email or email, role=user.role)
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}})


@api_bp.get("/auth/me")
@require_auth()
def me():
    auth = getattr(request, "auth", None)  # not used
    data = getattr(request, "g", None)
    # middleware/auth stores decoded JWT in flask.g
    from flask import g as _g

    auth_data = getattr(_g, "auth", {}) or {}
    email = auth_data.get("email", "")
    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "email": user.email, "role": user.role, "language": user.language})


@api_bp.get("/templates")
def templates():
    base = Path("generator/templates")
    names: list[str] = []
    if base.exists():
        for child in base.iterdir():
            if child.is_dir():
                names.append(child.name)
    return jsonify({"templates": sorted(names)})


@api_bp.get("/projects")
@require_auth()
def projects_list():
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    rows = list_requests_for_user_number(email, limit=200)
    payload: list[dict[str, Any]] = []
    for r in rows:
        payload.append(
            {
                "request_id": r.request_id,
                "status": r.status,
                "progress": r.progress,
                "website_type": r.website_type,
                "live_url": r.live_url,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return jsonify(payload)


@api_bp.get("/deployments")
@require_auth()
def deployments_list():
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    rows = list_deployments_for_user_number(email, limit=200)
    payload: list[dict[str, Any]] = []
    for r in rows:
        payload.append(
            {
                "request_id": r.request_id,
                "status": r.status,
                "url": r.url,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return jsonify(payload)


@api_bp.post("/projects")
@require_auth()
def projects_create():
    from flask import g as _g

    auth = _g.auth or {}
    email = auth.get("email", "")
    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    request_id = generate_request_id()
    create_request(request_id=request_id, user_number=email, message=message)
    enqueue_website_request(request_id=request_id, user_number=email, message=message, is_edit=False)
    return jsonify({"request_id": request_id, "status": "queued"})


@api_bp.get("/projects/<request_id>")
@require_auth()
def projects_get(request_id: str):
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    row = get_request(request_id)
    if not row or row.user_number != email:
        return jsonify({"error": "Not found"}), 404
    return jsonify(
        {
            "request_id": row.request_id,
            "status": row.status,
            "progress": row.progress,
            "website_type": row.website_type,
            "live_url": row.live_url,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
    )


@api_bp.post("/projects/<request_id>/edit")
@require_auth()
def projects_edit(request_id: str):
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    row = get_request(request_id)
    if not row or row.user_number != email:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    command = str(data.get("command") or "").strip()
    if not command:
        return jsonify({"error": "command is required"}), 400
    enqueue_website_request(request_id=request_id, user_number=email, message=command, is_edit=True)
    return jsonify({"request_id": request_id, "status": "rebuilding"})


@api_bp.get("/settings")
@require_auth()
def settings_get():
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"email": user.email, "role": user.role, "language": user.language, "whatsapp_number": user.whatsapp_number})


@api_bp.post("/settings/language")
@require_auth()
def settings_language_update():
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    data = request.get_json(silent=True) or {}
    language = str(data.get("language") or "").strip().lower()
    if language not in {"en", "es", "fr"}:
        return jsonify({"error": "Invalid language"}), 400
    user = update_user_by_email(email, language=language)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"ok": True, "language": user.language})


@api_bp.post("/settings/whatsapp")
@require_auth()
def settings_whatsapp_update():
    from flask import g as _g

    email = (_g.auth or {}).get("email", "")
    data = request.get_json(silent=True) or {}
    whatsapp_number = str(data.get("whatsapp_number") or "").strip()
    if not whatsapp_number:
        return jsonify({"error": "whatsapp_number required"}), 400
    user = update_user_by_email(email, whatsapp_number=whatsapp_number)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"ok": True, "whatsapp_number": user.whatsapp_number})


@api_bp.get("/projects/<request_id>/preview-url")
@require_auth()
def projects_preview_url(request_id: str):
    # Preview served by backend under /preview/<request_id>/
    return jsonify({"preview_url": f"/preview/{request_id}/"})


@api_bp.get("/projects/<request_id>/download")
@require_auth()
def projects_download(request_id: str):
    zip_path = Path("generated_sites") / f"{request_id}.zip"
    if not zip_path.exists():
        return jsonify({"error": "ZIP not found"}), 404
    return send_file(zip_path, as_attachment=True, download_name=f"{request_id}.zip")

