#!/usr/bin/env python3
"""Check the static delivery without a server, network or third-party packages."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = {"zh-hans": "zh-Hans", "zh-hant": "zh-Hant", "en": "en", "ja": "ja", "ko": "ko"}
PAGES = ("index.html", "privacy.html", "support.html")
ISSUES = "https://github.com/jacklv-coder/whimsy-cam-site/issues"
GITHUB_PRIVACY = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
MODELS = ("POP-55", "FOLD-58", "WIDE-88", "PULL-33", "FILM-1", "CCD-S", "DV-04", "STICKER", "PEEL", "CANDY")


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.source = path.read_text(encoding="utf-8")
        self.tags = []
        self.ids = []
        self.text = []
        self.feed(self.source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])

    def handle_data(self, text):
        self.text.append(text)

    def select(self, name):
        return [attrs for tag, attrs in self.tags if tag == name]


def check():
    harmony_privacy = ROOT / "zh-hans/harmony-privacy.html"
    expected = {ROOT / "index.html", harmony_privacy} | {ROOT / lang / page for lang in LANGUAGES for page in PAGES}
    actual = set(ROOT.glob("*.html")) | {p for lang in LANGUAGES for p in (ROOT / lang).glob("*.html")}
    assert expected == actual, f"Missing/extra pages: {expected ^ actual}"
    parsed = {path: Page(path) for path in sorted(expected)}
    references = 0
    external = set()
    for path, doc in parsed.items():
        assert doc.source.lower().startswith("<!doctype html>"), path
        assert len(doc.select("h1")) == 1, f"Expected one h1: {path}"
        assert len(doc.select("main")) == 1, f"Expected one main: {path}"
        assert all(n == 1 for n in Counter(doc.ids).values()), f"Duplicate IDs: {path}"
        assert any("width=device-width" in m.get("content", "") for m in doc.select("meta") if m.get("name") == "viewport"), path
        assert "© 2026 Jintao Lv" in doc.source, path
        assert not any(doc.select(t) for t in ("iframe", "object", "embed", "form", "base")), path
        for tag, attrs in doc.tags:
            assert not any(k.startswith("on") for k in attrs), f"Unexpected event handler: {path}"
            if tag == "img":
                assert "alt" in attrs and "width" in attrs and "height" in attrs, path
            if tag == "script":
                assert path == ROOT / "index.html" and "src" not in attrs, f"Unexpected script: {path}"
            for attr in ("href", "src"):
                if attr not in attrs:
                    continue
                ref = attrs[attr]
                assert ref, f"Empty {attr}: {path}"
                url = urlsplit(ref)
                if url.scheme or url.netloc:
                    assert tag == "a" and attr == "href", f"External resource: {path}: {ref}"
                    assert ref in (ISSUES, GITHUB_PRIVACY), f"Unexpected external link: {ref}"
                    external.add(ref)
                    continue
                assert not ref.startswith("/"), f"Not project-path portable: {path}: {ref}"
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                if target.is_dir():
                    target /= "index.html"
                assert target.is_relative_to(ROOT), f"Path escapes site: {path}: {ref}"
                assert target.is_file(), f"Broken link/resource: {path}: {ref}"
                if url.fragment:
                    assert target in parsed and unquote(url.fragment) in parsed[target].ids, f"Missing fragment: {path}: {ref}"
                references += 1
        if path.parent == ROOT:
            assert len(doc.select("script")) == 1
            for lang in LANGUAGES:
                assert any(a.get("href") == f"{lang}/index.html" for a in doc.select("a"))
            continue
        lang = path.parent.name
        assert doc.select("html")[0]["lang"] == LANGUAGES[lang], path
        assert not doc.select("script"), path
        if path == harmony_privacy:
            assert any(t.get("datetime") == "2026-10-09" for t in doc.select("time")), path
            assert all(section in doc.ids for section in ("local-content", "permissions", "device-data", "sharing", "storage", "rights", "children", "website")), path
            assert ISSUES in doc.source and GITHUB_PRIVACY in doc.source, path
            assert len(doc.select("strong")) >= 2, path
            continue
        for other, hreflang in LANGUAGES.items():
            matches = [a for a in doc.select("a") if a.get("hreflang") == hreflang]
            assert len(matches) == 1 and matches[0]["href"] == f"../{other}/{path.name}", f"Wrong language switch: {path} -> {other}"
            assert matches[0].get("lang") == hreflang
            assert (matches[0].get("aria-current") == "true") == (lang == other)
        assert len([a for a in doc.select("a") if a.get("aria-current") == "page"]) == 1, path
        for page in PAGES:
            assert any(a.get("href") == page for a in doc.select("a")), f"Missing navigation: {path}: {page}"
        if path.name == "support.html":
            assert len(doc.select("details")) == len(doc.select("summary")) == 12, path
            assert all(f"faq-{i}" in doc.ids for i in range(1, 13)), path
            assert "iOS 17" in doc.source and ISSUES in doc.source, path
        elif path.name == "privacy.html":
            assert all(f"policy-{i}" in doc.ids for i in range(1, 12)), path
            assert any(t.get("datetime") == "2026-10-07" for t in doc.select("time")), path
            assert all(s in doc.source for s in ("Jintao Lv", "iCloud", "Apple", "GitHub Pages", "SDK", ISSUES, GITHUB_PRIVACY)), path
        else:
            assert all(model in doc.source for model in MODELS), path
            assert len(doc.select("img")) == 4, path
            assert "apps.apple.com" not in doc.source, path
    css = (ROOT / "style.css").read_text()
    assert not re.search(r"@import|@font-face|url\s*\(", css, re.I), "Unexpected font or CSS dependency"
    assert not re.search(r"overflow-x\s*:\s*(hidden|clip)", css), "Do not hide overflow to pass layout checks"
    assert (ROOT / ".nojekyll").is_file()
    icon = (ROOT / "icon.png").read_bytes()
    assert icon[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", icon[16:24]) == (256, 256)
    print(f"PASS: {len(parsed)} HTML pages, {references} local links/resources, 75 same-page language switches.")
    print("PASS: 60 FAQs, 55 iOS + 8 HarmonyOS privacy sections, ten camera models per homepage, icon 256×256.")
    print("PASS: no external resources, scripts, fonts, forms or embedded frames; content pages need no JS.")
    print("External links (not network-validated by this check):")
    for link in sorted(external):
        print(f"  {link}")
    print("375px rendering requires a separate browser check; this script does not measure layout.")


if __name__ == "__main__":
    check()
