from __future__ import annotations

import os

import requests

from utils.constants import REQUEST_TIMEOUT_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)


def transcribe_audio_url(media_url: str) -> str:
    """Transcribe voice note using Groq Whisper-compatible endpoint when configured."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return ""

    try:
        audio = requests.get(media_url, timeout=REQUEST_TIMEOUT_SECONDS)
        audio.raise_for_status()
        files = {"file": ("audio.ogg", audio.content, "audio/ogg")}
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data={"model": "whisper-large-v3"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as exc:
        logger.warning("Voice transcription failed: %s", exc)
        return ""
