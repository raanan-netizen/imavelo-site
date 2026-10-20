"""Checks the built site before it is published.

- every page: <html lang dir>, charset, viewport, title, description, canonical, one <h1>;
- English and Hebrew versions of every page exist and link to each other; Hebrew pages are right-to-left;
- every internal link points to a built page or asset;
- nothing is loaded from another site (no external scripts, styles, fonts, images or frames);
- no secrets or personal data patterns (keys, tokens, card numbers, phone-like numbers, e-mail addresses
  other than the configured contact addresses);
- placeholders still to fill (class="todo") are listed; with --publish any placeholder is an error.

    python3 tools/check_site.py [--publish]
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISH = "--publish" in sys.argv[1:]
SKIP = {".git", "src", "tools", "node_modules"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.attrs, self.links, self.loads, self.todo, self.h1 = [], {}, [], [], [], 0
        self._todo = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "html":
            self.attrs["html"] = a
        if tag == "meta" and a.get("name") in ("viewport", "description"):
            self.attrs[a["name"]] = a.get("content", "")
        if tag == "meta" and "charset" in a:
            self.attrs["charset"] = a["charset"]
        if tag == "link" and a.get("rel") == "canonical":
            self.attrs["canonical"] = a.get("href")
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("script", "img", "iframe", "source", "video", "audio", "embed", "object") or (tag == "link" and a.get("rel") == "stylesheet"):
            self.loads.append(a.get("src") or a.get("href") or tag)
        if a.get("class") == "todo":
            self._todo = True

    def handle_endtag(self, tag):
        if tag == "span":
            self._todo = False

    def handle_data(self, data):
        self.text.append(data)
        if self._todo:
            self.todo.append(data.strip())


def pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            if f == "index.html":
                yield os.path.join(d, f)


def to_path(href, here):
    href = href.split("#")[0]
    if not href or href.startswith(("mailto:", "https://", "http://")):
        return None
    base = "/" + os.path.relpath(os.path.dirname(here), ROOT).replace("\\", "/").strip(".") + "/"
    p = href if href.startswith("/") else base + href
    p = os.path.join(ROOT, *[x for x in p.split("/") if x])
    return os.path.join(p, "index.html") if not os.path.splitext(p)[1] else p


SECRETS = [
    (r"goog_[A-Za-z0-9]{10,}", "RevenueCat key"),
    (r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S{8,}", "credential-like assignment"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"\b(?:\d[ -]?){13,19}\b", "card-like number"),
    (r"\+?\d{3}[ -]?\d{2,3}[ -]?\d{3}[ -]?\d{3,4}", "phone-like number"),
]
ALLOWED_EMAILS = set(filter(None, os.environ.get("SITE_EMAILS", "").split(",")))

errors, todos = [], []
found = list(pages())
for path in sorted(found):
    rel = "/" + os.path.relpath(path, ROOT).replace("\\", "/").replace("index.html", "")
    src = open(path, encoding="utf-8").read()
    p = Page()
    p.feed(src)
    h = p.attrs.get("html", {})
    lang = h.get("lang")
    if lang not in ("en", "he"):
        errors.append(f"{rel}: <html lang> is {lang!r}")
    if lang == "he" and h.get("dir") != "rtl":
        errors.append(f"{rel}: Hebrew page is not dir=rtl")
    if lang == "en" and h.get("dir") != "ltr":
        errors.append(f"{rel}: English page is not dir=ltr")
    for need in ("charset", "viewport", "description", "canonical"):
        if not p.attrs.get(need):
            errors.append(f"{rel}: missing {need}")
    if "width=device-width" not in p.attrs.get("viewport", ""):
        errors.append(f"{rel}: viewport is not mobile-friendly")
    if p.h1 != 1:
        errors.append(f"{rel}: {p.h1} <h1> elements")
    if not (p.attrs.get("canonical") or "").startswith("https://"):
        errors.append(f"{rel}: canonical is not https")
    for load in p.loads:
        if not str(load).startswith("/"):
            errors.append(f"{rel}: loads an external or inline resource: {load}")
    for href in p.links:
        if href.startswith("http://"):
            errors.append(f"{rel}: insecure link {href}")
        target = to_path(href, path)
        if target and not os.path.exists(target):
            errors.append(f"{rel}: broken link {href}")
    other = rel.replace("/he/", "/") if "/he/" in rel or rel == "/he/" else rel + "he/"
    if not os.path.exists(os.path.join(ROOT, *[x for x in other.split("/") if x], "index.html")):
        errors.append(f"{rel}: no counterpart page {other}")
    text = " ".join(p.text)
    for pattern, label in SECRETS:
        for m in re.finditer(pattern, text):
            errors.append(f"{rel}: {label}: {m.group(0)[:24]}")
    for m in re.finditer(r"[\w.+-]+@[\w-]+\.[\w.]+", text):
        if m.group(0) not in ALLOWED_EMAILS:
            errors.append(f"{rel}: e-mail address not configured as a site contact: {m.group(0)}")
    todos += [f"{rel}: {t}" for t in p.todo]

print(f"{len(found)} pages checked")
if todos:
    print(f"{len(todos)} placeholders to fill:")
    for t in todos:
        print("  " + t)
for e in errors:
    print("ERROR " + e)
if PUBLISH and todos:
    print("ERROR placeholders remain; not ready to publish")
sys.exit(1 if errors or (PUBLISH and todos) else 0)
