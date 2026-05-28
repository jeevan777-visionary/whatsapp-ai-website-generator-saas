from __future__ import annotations

import hmac
import os
from hashlib import sha256


def mask_secret(secret: str) -> str:
    if len(secret) <= 6:
        return "***"
    return f"{secret[:3]}***{secret[-2:]}"


def sign_payload(payload: str) -> str:
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    return hmac.new(token.encode(), payload.encode(), sha256).hexdigest()
