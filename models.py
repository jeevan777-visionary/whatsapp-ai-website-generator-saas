from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    whatsapp_number: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WebsiteRequest(Base):
    __tablename__ = "website_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_number: Mapped[str] = mapped_column(String(50), index=True)
    raw_message: Mapped[str] = mapped_column(Text)
    extracted_json: Mapped[str] = mapped_column(Text, default="{}")
    content_json: Mapped[str] = mapped_column(Text, default="{}")
    website_type: Mapped[str] = mapped_column(String(30), default="agency")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    live_url: Mapped[str] = mapped_column(String(255), default="")
    site_slug: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GeneratedWebsite(Base):
    __tablename__ = "generated_websites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_number: Mapped[str] = mapped_column(String(50), index=True)
    business_name: Mapped[str] = mapped_column(String(120), default="")
    template_type: Mapped[str] = mapped_column(String(30), default="agency")
    zip_path: Mapped[str] = mapped_column(String(255), default="")
    preview_path: Mapped[str] = mapped_column(String(255), default="")
    live_url: Mapped[str] = mapped_column(String(255), default="")
    netlify_site_id: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DeploymentLog(Base):
    __tablename__ = "deployment_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(255), default="")
    netlify_deploy_id: Mapped[str] = mapped_column(String(80), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EditHistory(Base):
    __tablename__ = "edit_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(50), index=True)
    user_number: Mapped[str] = mapped_column(String(50), index=True)
    command: Mapped[str] = mapped_column(Text)
    changes_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    request_id: Mapped[str] = mapped_column(String(50), default="")
    user_number: Mapped[str] = mapped_column(String(50), default="")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DeploymentStatus(Base):
    __tablename__ = "deployment_statuses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phase: Mapped[str] = mapped_column(String(40), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(255), default="")
    live_url: Mapped[str] = mapped_column(String(255), default="")
    error: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
