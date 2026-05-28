from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, EmailStr, Field

import database.db as db_module
from ai.transcription import transcribe_audio_url
from database.db import init_db
from database.models import DeploymentStatus
from database.models import User
from database.repository import (
    create_request,
    get_request,
    get_user_by_email,
    list_requests_for_user_number,
    update_user_by_email,
)
from tasks.generation_tasks import enqueue_website_request
from utils.auth import create_access_token, decode_access_token, hash_password, verify_password
from utils.helpers import generate_request_id
from utils.logger import configure_logging, get_logger
from whatsapp.handlers import handle_incoming_message

load_dotenv()
configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="WhatsApp AI Website Generator API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db(os.getenv("DATABASE_URL", "sqlite:///app.db"))


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProjectCreateIn(BaseModel):
    message: str = Field(min_length=4, max_length=4000)


class EditIn(BaseModel):
    command: str = Field(min_length=2, max_length=500)


def _auth_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(payload.get("email", ""))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi-backend"}


@app.post("/api/v2/auth/signup")
def signup(payload: SignupIn):
    existing = get_user_by_email(payload.email.lower())
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")
    db = db_module.SessionLocal()
    try:
        user = User(
            whatsapp_number=payload.email.lower(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role="user",
            language="en",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    finally:
        db.close()
    token = create_access_token(user_id=user.id, email=user.email or "", role=user.role)
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}}


@app.post("/api/v2/auth/login")
def login(payload: LoginIn):
    user = get_user_by_email(payload.email.lower())
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user_id=user.id, email=user.email or "", role=user.role)
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}}


@app.get("/api/v2/projects")
def list_projects(user=Depends(_auth_user)):
    rows = list_requests_for_user_number(user.email or user.whatsapp_number, limit=300)
    return [
        {
            "request_id": row.request_id,
            "status": row.status,
            "progress": row.progress,
            "website_type": row.website_type,
            "live_url": row.live_url,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


@app.post("/api/v2/projects")
def create_project(payload: ProjectCreateIn, user=Depends(_auth_user)):
    request_id = generate_request_id()
    owner = user.email or user.whatsapp_number
    create_request(request_id=request_id, user_number=owner, message=payload.message)
    enqueue_website_request(request_id=request_id, user_number=owner, message=payload.message, is_edit=False)
    return {"request_id": request_id, "status": "queued"}


@app.post("/api/v2/projects/{request_id}/edit")
def edit_project(request_id: str, payload: EditIn, user=Depends(_auth_user)):
    row = get_request(request_id)
    owner = user.email or user.whatsapp_number
    if not row or row.user_number != owner:
        raise HTTPException(status_code=404, detail="Project not found")
    enqueue_website_request(request_id=request_id, user_number=owner, message=payload.command, is_edit=True)
    return {"request_id": request_id, "status": "rebuilding"}


@app.get("/api/v2/projects/{request_id}/download")
def download_project(request_id: str, user=Depends(_auth_user)):
    row = get_request(request_id)
    owner = user.email or user.whatsapp_number
    if not row or row.user_number != owner:
        raise HTTPException(status_code=404, detail="Project not found")
    zip_path = Path("generated_sites") / f"{request_id}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP not found")
    return FileResponse(zip_path, filename=f"{request_id}.zip")


@app.post("/api/v2/settings/language")
def set_language(payload: dict[str, Any], user=Depends(_auth_user)):
    language = str(payload.get("language", "")).lower()
    if language not in {"en", "es", "fr"}:
        raise HTTPException(status_code=400, detail="Invalid language")
    updated = update_user_by_email(user.email or "", language=language)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "language": updated.language}


@app.post("/api/v2/whatsapp/incoming")
def whatsapp_incoming(payload: dict[str, Any]):
    frm = str(payload.get("from", "")).strip()
    body = str(payload.get("body", "")).strip()
    if not frm or not body:
        raise HTTPException(status_code=400, detail="from/body required")
    request_id = handle_incoming_message(frm, body)
    return {"request_id": request_id, "status": "accepted"}


@app.post("/api/v2/voice/transcribe")
async def voice_transcribe(media_url: str | None = None, file: UploadFile | None = File(default=None)):
    if media_url:
        text = transcribe_audio_url(media_url)
        return {"text": text}
    if file is not None:
        # For now, if raw file upload is used, persist temp and return basic ack.
        data = await file.read()
        return {"size": len(data), "filename": file.filename}
    raise HTTPException(status_code=400, detail="media_url or file required")


@app.websocket("/ws/v2/progress/{request_id}")
async def ws_progress(websocket: WebSocket, request_id: str):
    await websocket.accept()
    try:
        while True:
            if db_module.SessionLocal is None:
                await websocket.send_json({"error": "db unavailable"})
                await websocket.close()
                break
            db = db_module.SessionLocal()
            try:
                row = db.query(DeploymentStatus).filter_by(request_id=request_id).first()
                if not row:
                    await websocket.send_json({"request_id": request_id, "phase": "queued", "progress": 0})
                else:
                    await websocket.send_json(
                        {
                            "request_id": request_id,
                            "phase": row.phase,
                            "progress": row.progress,
                            "message": row.message,
                            "live_url": row.live_url,
                            "error": row.error,
                        }
                    )
                    if row.phase in {"completed", "failed"} or (row.progress or 0) >= 100:
                        await websocket.close()
                        break
            finally:
                db.close()
            import asyncio

            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for %s", request_id)

