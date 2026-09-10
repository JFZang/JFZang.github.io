from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
FALLBACK_ROOT = Path(r"C:\Users\jiefu\Documents\GitHub\JFZang.github.io")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.ids: list[str] = []
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "meta" and values.get("name", "").lower() == "viewport":
            self.has_viewport = True


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


pages = sorted(ROOT.rglob("*.html"))
parsed = {page: parse_page(page) for page in pages}
errors: list[str] = []

# Reader-facing publication pages that must remain discoverable from the home page.
# This prevents a later index.html overwrite from silently orphaning published work.
required_home_links = {
    "projects/zeta-global-stock-thesis.html",
    "projects/enterprise-marketing-data-platforms.html",
    "projects/china-baijiu-industry-primer.html",
}

required_home_anchors = {
    "#stock-research",
    "#industry-research",
    "#macro",
    "#market-notes",
    "#glossary",
    "#projects",
    "#contact",
}

home_page = ROOT / "index.html"
if home_page.exists():
    home_hrefs = {
        unquote(urlsplit(href).path).replace("\\", "/")
        for href in parsed[home_page].hrefs
    }
    for required_link in sorted(required_home_links):
        required_page = ROOT / required_link
        if required_page.exists() and required_link not in home_hrefs:
            errors.append(f"index.html: published page is missing from home page: {required_link}")
    for required_anchor in sorted(required_home_anchors):
        if required_anchor not in parsed[home_page].hrefs:
            errors.append(f"index.html: primary navigation entry is missing: {required_anchor}")
        if required_anchor[1:] not in parsed[home_page].ids:
            errors.append(f"index.html: primary section is missing: {required_anchor}")

for page, parser in parsed.items():
    rel = page.relative_to(ROOT)
    if not parser.has_viewport:
        errors.append(f"{rel}: missing viewport meta tag")
    duplicate_ids = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicate_ids:
        errors.append(f"{rel}: duplicate ids {duplicate_ids}")

    for raw_href in parser.hrefs:
        split = urlsplit(raw_href)
        if split.scheme in {"http", "https", "mailto", "tel"}:
            continue
        if raw_href.startswith("#"):
            if split.fragment and split.fragment not in parser.ids:
                errors.append(f"{rel}: missing local fragment #{split.fragment}")
            continue

        target = (page.parent / unquote(split.path)).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"{rel}: link escapes staged site: {raw_href}")
            continue
        if not target.exists():
            fallback_target = (FALLBACK_ROOT / target.relative_to(ROOT)).resolve()
            if not fallback_target.exists():
                errors.append(f"{rel}: missing target {raw_href}")
                continue
            target = fallback_target
        if split.fragment and target.suffix.lower() == ".html":
            target_parser = parsed.get(target) or parse_page(target)
            if split.fragment not in target_parser.ids:
                errors.append(f"{rel}: target fragment missing {raw_href}")

print(f"Checked {len(pages)} HTML pages")
print(f"Checked {sum(len(parser.hrefs) for parser in parsed.values())} links")
if errors:
    print("FAIL")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print("PASS: internal files, fragments, viewport tags and duplicate IDs")
