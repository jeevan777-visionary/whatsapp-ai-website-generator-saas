from __future__ import annotations

import os
import json
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, send_from_directory
from flask_cors import CORS
from flask_sock import Sock

from database.db import init_db
from dashboard.routes import dashboard_bp
from middleware.security import register_security_middleware
from tasks.celery_worker import make_celery
from tasks.generation_tasks import register_tasks
from utils.logger import configure_logging, get_logger
from whatsapp.webhook import whatsapp_bp
from api.routes import api_bp
import database.db as db_module
from database.models import DeploymentStatus
import time

load_dotenv()
configure_logging()
logger = get_logger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.config["TWILIO_WHATSAPP_NUMBER"] = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    init_db(app.config["DATABASE_URL"])
    CORS(
        app,
        resources={
            r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]},
            r"/health": {"origins": "*"},
        },
        supports_credentials=True,
    )
    register_security_middleware(app)
    sock = Sock(app)

    app.register_blueprint(whatsapp_bp, url_prefix="/webhook")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    @app.get("/preview/<request_id>/")
    def preview_index(request_id: str):
        base = Path("generated_sites") / request_id
        if not base.exists():
            return jsonify({"error": "Preview not found"}), 404
        return send_from_directory(base, "index.html")

    @app.get("/preview/<request_id>/<path:filename>")
    def preview_static(request_id: str, filename: str):
        base = Path("generated_sites") / request_id
        if not base.exists():
            return jsonify({"error": "Preview not found"}), 404
        # Prevent path traversal via Flask send_from_directory's internal checks.
        return send_from_directory(base, filename)

    @sock.route("/ws/progress/<request_id>")
    def ws_progress(ws, request_id: str):
        # Periodically poll DB and stream progress updates.
        while True:
            if db_module.SessionLocal is None:
                ws.send(json.dumps({"error": "db unavailable"}))
                time.sleep(2)
                continue
            db = db_module.SessionLocal()
            try:
                row = db.query(DeploymentStatus).filter_by(request_id=request_id).first()
                if not row:
                    ws.send(json.dumps({"request_id": request_id, "phase": "queued", "progress": 0}))
                else:
                    ws.send(
                        json.dumps(
                            {
                                "request_id": request_id,
                                "phase": row.phase,
                                "progress": row.progress,
                                "message": row.message,
                                "live_url": row.live_url,
                                "error": row.error,
                            }
                        )
                    )
                    if row.phase in {"completed", "failed"} or (row.progress or 0) >= 100:
                        break
            finally:
                db.close()
            time.sleep(2.0)

    @app.get("/dashboard")
    def dashboard_redirect():
        return redirect("/dashboard/")

    @app.get("/")
    def root():
        return redirect("/dashboard/")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "whatsapp-ai-website-generator"}), 200

    return app


flask_app = create_app()
celery_app = make_celery(flask_app)
process_website_request = register_tasks(celery_app)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    logger.info("Starting Flask server on port %s", port)
    flask_app.run(host="0.0.0.0", port=port, debug=flask_app.config["DEBUG"])
