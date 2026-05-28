from __future__ import annotations

import json
import os
import requests

from ai.prompts import CONTENT_PROMPT
from utils.constants import REQUEST_TIMEOUT_SECONDS


def generate_content(requirements: dict) -> dict:
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    if not api_key:
        return default_content(requirements)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CONTENT_PROMPT},
            {"role": "user", "content": json.dumps(requirements)},
        ],
        "temperature": 0.7,
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
        fallback = default_content(requirements)
        # Ensure generator templates never crash due to missing keys.
        merged = dict(fallback)
        merged.update({k: v for k, v in parsed.items() if v is not None})
        if "hero" not in merged:
            merged["hero"] = fallback["hero"]
        if "services" not in merged:
            merged["services"] = fallback["services"]
        if "footer" not in merged:
            merged["footer"] = fallback["footer"]
        return merged
    except Exception:
        return default_content(requirements)


def default_content(requirements: dict) -> dict:
    name = requirements.get("business_name", "Your Brand")
    return {
        "hero": {"headline": f"{name} That Moves Business Forward", "subheading": "Built for trust and conversion."},
        "about": f"{name} delivers premium digital experiences tailored to your audience.",
        "services": ["Strategy", "Design", "Development", "Optimization"],
        "testimonials": [{"quote": "Excellent quality and delivery.", "author": "Happy Client"}],
        "faqs": [{"q": "How fast can we launch?", "a": "Most sites launch in days."}],
        "cta": "Book a consultation today.",
        "footer": f"© {name}. All rights reserved.",
    }
