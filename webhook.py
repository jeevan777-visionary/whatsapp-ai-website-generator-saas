from __future__ import annotations

import os

from flask import Blueprint, jsonify, request
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from utils.rate_limiter import InMemoryRateLimiter
from whatsapp.handlers import handle_incoming_message, handle_voice_message

whatsapp_bp = Blueprint("whatsapp", __name__)
limiter = InMemoryRateLimiter(limit=20, window_seconds=60)


def _validate_twilio_request() -> bool:
    validate = os.getenv("TWILIO_VALIDATE_SIGNATURE", "true").lower() == "true"
    if not validate:
        return True
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    signature = request.headers.get("X-Twilio-Signature", "")
    if not auth_token:
        return True
    if not signature and os.getenv("DEBUG", "false").lower() == "true":
        return True
    validator = RequestValidator(auth_token)
    # Twilio signature validation can break behind proxies/tunnels if URL differs.
    candidates = [request.url]
    configured_webhook = os.getenv("WEBHOOK_URL", "").strip()
    if configured_webhook:
        candidates.append(configured_webhook)
    if request.url.startswith("http://"):
        candidates.append(request.url.replace("http://", "https://", 1))
    if configured_webhook.startswith("http://"):
        candidates.append(configured_webhook.replace("http://", "https://", 1))
    for candidate in dict.fromkeys(candidates):
        if validator.validate(candidate, request.form, signature):
            return True
    return False


@whatsapp_bp.post("/whatsapp")
def receive_whatsapp():
    if not _validate_twilio_request():
        return jsonify({"error": "Invalid signature"}), 403

    from_number = request.form.get("From", "").strip()
    body = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", "0") or 0)

    if not from_number:
        return jsonify({"error": "Invalid payload"}), 400
    if not limiter.allow(from_number):
        return jsonify({"error": "Rate limit exceeded"}), 429

    if num_media > 0:
        media_url = request.form.get("MediaUrl0", "")
        media_type = request.form.get("MediaContentType0", "")
        if media_type.startswith("audio/") and media_url:
            request_id = handle_voice_message(from_number, media_url)
            response = MessagingResponse()
            response.message("Voice received. Processing your website request...")
            return str(response), 200, {"Content-Type": "application/xml"}

    if not body:
        return jsonify({"error": "Message body required"}), 400

    request_id = handle_incoming_message(from_number, body)
    response = MessagingResponse()
    response.message(f"Request accepted. Tracking ID: {request_id[:8]}")
    return str(response), 200, {"Content-Type": "application/xml"}
