from __future__ import annotations

import json
import os
import requests

from ai.fallback import fallback_requirements
from ai.prompts import EXTRACTION_PROMPT
from ai.validator import normalize_requirements
from utils.constants import REQUEST_TIMEOUT_SECONDS
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_requirements(message: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    if not api_key:
        return fallback_requirements(message)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return normalize_requirements(parsed)
    except Exception as exc:
        logger.exception("AI extraction failed: %s", exc)
        return fallback_requirements(message)
