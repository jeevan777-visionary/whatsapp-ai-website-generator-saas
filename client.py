from __future__ import annotations

import os
from twilio.rest import Client

from utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppClient:
    def __init__(self):
        self.client = None
        self.from_number = ""
        self._ensure_client()

    def _ensure_client(self) -> None:
        sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip()
        self.client = Client(sid, token) if sid and token else None

    def send_message(self, to: str, message: str) -> None:
        # Refresh creds each call so .env changes are picked up after startup.
        self._ensure_client()
        if not to.startswith("whatsapp:"):
            logger.info("Skipping non-WhatsApp recipient: %s", to)
            return
        if not self.client:
            logger.warning("Twilio client not configured. Skipping outbound message.")
            return
        try:
            self.client.messages.create(body=message, from_=self.from_number, to=to)
        except Exception as exc:
            # Notifications must never break the generation pipeline.
            logger.error("Failed to send WhatsApp message to %s: %s", to, exc)
