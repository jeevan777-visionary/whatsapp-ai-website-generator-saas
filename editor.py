from __future__ import annotations


def apply_edit_command(requirements: dict, content: dict, intent: dict) -> tuple[dict, dict]:
    requirements = dict(requirements)
    content = dict(content)

    if intent.get("color_scheme"):
        requirements["color_scheme"] = intent["color_scheme"]
    if intent.get("website_type"):
        requirements["website_type"] = intent["website_type"]
    if intent.get("style"):
        requirements["style"] = intent["style"]
    if intent.get("language"):
        requirements["language"] = intent["language"]

    if intent.get("section_order"):
        # Editor UI reorders sections; generator templates render in this exact order.
        requirements["required_sections"] = list(intent["section_order"])

    if intent.get("add_section") == "testimonials":
        content.setdefault("testimonials", [])
        content["testimonials"].append({"quote": "Outstanding service.", "author": "Client"})
    if intent.get("add_section") == "faqs":
        content.setdefault("faqs", [])
        content["faqs"].append({"q": "How can I contact you?", "a": "Use the contact form below."})

    if intent.get("target") == "header" and "hero" in content:
        hero = dict(content.get("hero", {}))
        hero["headline"] = f"{requirements.get('business_name', 'Your Brand')} — Updated"
        content["hero"] = hero

    return requirements, content
