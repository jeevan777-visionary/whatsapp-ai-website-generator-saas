from __future__ import annotations

from utils.constants import DEFAULT_SECTIONS


def fallback_requirements(message: str) -> dict:
    lower = message.lower()
    website_type = "agency"
    for candidate in ("restaurant", "portfolio", "store", "blog", "saas"):
        if candidate in lower:
            website_type = candidate
            break

    name = "Elevate Studio"
    for token in message.split():
        if token[0].isupper() and len(token) > 2:
            name = token.strip(".,!")
            break

    return {
        "website_type": website_type,
        "business_name": name,
        "business_category": "digital services",
        "color_scheme": "dark",
        "style": "modern premium",
        "tone": "confident",
        "required_sections": DEFAULT_SECTIONS,
        "required_features": ["responsive", "seo", "contact form", "animations"],
        "target_audience": "business owners",
        "contact_information": {"email": "hello@example.com", "phone": "+1 000 000 0000"},
        "social_links": {},
        "preferred_layout": "single-page",
        "animation_preferences": "subtle motion",
        "source_message": message,
    }
