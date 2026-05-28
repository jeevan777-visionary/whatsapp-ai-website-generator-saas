from __future__ import annotations


COLOR_MAP = {
    "blue": "#2563eb",
    "red": "#dc2626",
    "green": "#16a34a",
    "dark": "#111827",
    "warm": "#b45309",
    "indigo": "#4f46e5",
}


def generate_logo_svg(business_name: str, color_scheme: str = "indigo") -> str:
    color = COLOR_MAP.get(color_scheme, COLOR_MAP["indigo"])
    initials = "".join(part[0] for part in business_name.split()[:2]).upper() or "WB"
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'>
  <rect width='64' height='64' rx='14' fill='{color}'/>
  <text x='50%' y='54%' text-anchor='middle' fill='white' font-size='24' font-family='Inter, sans-serif' font-weight='700'>{initials}</text>
</svg>"""
