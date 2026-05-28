from __future__ import annotations

import re

EDIT_KEYWORDS = (
    "make",
    "change",
    "update",
    "add",
    "remove",
    "switch",
    "set",
    "use template",
    "template",
)


def is_edit_command(message: str) -> bool:
    lower = message.lower().strip()
    if lower.startswith("/edit"):
        return True
    return any(lower.startswith(k) or f" {k} " in f" {lower} " for k in EDIT_KEYWORDS)


def parse_edit_intent(message: str) -> dict:
    lower = message.lower()
    intent: dict = {"raw": message}

    # Theme updates (supports both "blue" and "make theme blue" styles).
    if "blue" in lower:
        intent["color_scheme"] = "blue"
    elif "red" in lower:
        intent["color_scheme"] = "red"
    elif "green" in lower:
        intent["color_scheme"] = "green"
    elif "dark" in lower:
        intent["color_scheme"] = "dark"
    elif "indigo" in lower:
        intent["color_scheme"] = "indigo"
    elif "warm" in lower:
        intent["color_scheme"] = "warm"

    if "testimonial" in lower:
        intent["add_section"] = "testimonials"
    if "faq" in lower:
        intent["add_section"] = "faqs"
    if "header" in lower:
        intent["target"] = "header"

    template_match = re.search(r"template\s+(restaurant|portfolio|store|blog|agency|saas)", lower)
    if template_match:
        intent["website_type"] = template_match.group(1)

    if "font" in lower:
        intent["style"] = "modern serif" if "serif" in lower else "clean sans"

    lang_match = re.search(r"language\s+([a-z]{2})", lower)
    if lang_match:
        intent["language"] = lang_match.group(1)

    # Section ordering: "Reorder sections: hero, about, services"
    reorder_match = re.search(r"reorder sections\s*:\s*([^.\n\r]+)", lower)
    if reorder_match:
        raw = reorder_match.group(1)
        parts = [p.strip() for p in re.split(r"[,\s]+", raw) if p.strip()]
        allowed = {"hero", "about", "services", "testimonials", "faqs", "contact", "footer"}
        section_order = [p for p in parts if p in allowed]
        if section_order:
            intent["section_order"] = section_order

    return intent
