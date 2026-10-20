"""Builds the static Imavelo site from src/ fragments into published folders (GitHub Pages serves the repo root).

Each page has an English and a Hebrew fragment: src/<slug>.en.html and src/<slug>.he.html (body content only).
English is published at /<path>/, Hebrew at /<path>/he/ (the home page: / and /he/).

    python3 tools/build.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://imavelo.com"

# slug, path, English title, Hebrew title
PAGES = [
    ("home", "", "Imavelo", "Imavelo"),
    ("parklast", "parklast", "ParkLast", "ParkLast"),
    ("privacy", "parklast/privacy", "ParkLast Privacy Policy", "מדיניות הפרטיות של ParkLast"),
    ("terms", "parklast/terms", "ParkLast Terms of Service", "תנאי השימוש של ParkLast"),
    ("support", "parklast/support", "ParkLast Support", "תמיכה ב־ParkLast"),
]

NAV = {
    "en": [("parklast", "ParkLast"), ("parklast/privacy", "Privacy"), ("parklast/terms", "Terms"), ("parklast/support", "Support")],
    "he": [("parklast", "ParkLast"), ("parklast/privacy", "פרטיות"), ("parklast/terms", "תנאי שימוש"), ("parklast/support", "תמיכה")],
}


def url(path, lang):
    base = "/" + (path + "/" if path else "")
    return base + ("he/" if lang == "he" else "")


def page(slug, path, title, lang):
    body = open(os.path.join(ROOT, "src", f"{slug}.{lang}.html"), encoding="utf-8").read()
    other = "he" if lang == "en" else "en"
    direction = "rtl" if lang == "he" else "ltr"
    current = ' aria-current="page"'
    nav = "".join(
        '<a href="{}"{}>{}</a>'.format(url(p, lang), current if p == path else "", html.escape(label))
        for p, label in NAV[lang]
    )
    switch = '<a class="lang" href="{}" hreflang="{}" lang="{}">{}</a>'.format(
        url(path, other), other, other, "עברית" if other == "he" else "English")
    m = re.search(r"<p class=\"lead\">(.*?)</p>", body, re.S)
    description = html.escape(re.sub(r"<[^>]+>", "", m.group(1)).strip()) if m else html.escape(title)
    footer = ("© Imavelo · " if lang == "en" else "© Imavelo · ") + nav
    return f"""<!doctype html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{SITE}{url(path, lang)}">
<link rel="alternate" hreflang="en" href="{SITE}{url(path, 'en')}">
<link rel="alternate" hreflang="he" href="{SITE}{url(path, 'he')}">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="{url('', lang)}">Imavelo</a><nav>{nav}</nav>{switch}</div></header>
<main class="wrap">
{body.strip()}
</main>
<footer class="wrap">{footer}</footer>
</body>
</html>
"""


def main():
    for slug, path, en, he in PAGES:
        for lang, title in (("en", en), ("he", he)):
            out_dir = os.path.join(ROOT, *[p for p in path.split("/") if p], *(["he"] if lang == "he" else []))
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
                f.write(page(slug, path, title, lang))
            print("built", url(path, lang))


if __name__ == "__main__":
    main()
