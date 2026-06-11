#!/usr/bin/env python3
"""
Generate a recommended ``llms.txt`` for the analyzed target website.

This reads the sitemap analysis produced by ``collect_data.py`` and emits a
root ``llms.txt`` for the *analyzed site* (not for this project), following the
emerging llmstxt.org convention: a short, curated, Markdown index of a site's
most important entry points so that LLM-based tools and AI agents can discover
them quickly.

IMPORTANT: ``llms.txt`` is OPTIONAL. It is NOT a Google Search requirement and
does not affect Google ranking. It is a convenience for AI/agent tooling.

Date: December 7, 2025
"""

import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from utils.path_manager import get_current_project_path, get_latest_file

# URL categories (from collect_data.categorize_url) mapped to llms.txt sections,
# in the order they should appear. "static"/"other" are folded into Key pages.
SECTION_ORDER = [
    ("product", "Products & services"),
    ("category", "Categories"),
    ("content", "Content & resources"),
]

# Per-section cap so the file stays short and curated (the spirit of llms.txt).
MAX_LINKS_PER_SECTION = 15


def _safe_link_url(url):
    """Return a clean http(s) URL safe to embed in a Markdown link, or None.

    Sitemap URLs are externally controlled, so reject unsafe schemes (e.g.
    ``javascript:``), control characters/whitespace, and parentheses that
    would break Markdown link syntax.
    """
    if not url:
        return None
    url = str(url).strip()
    if any((ord(c) < 0x20) or c.isspace() for c in url):
        return None
    if "(" in url or ")" in url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def _safe_filename_stem(domain):
    """Confine a domain-derived filename to the project directory.

    Strips path separators and traversal so the output can only ever be
    written inside the resolved reports directory.
    """
    stem = re.sub(r"[^A-Za-z0-9.-]", "_", str(domain or "").strip())
    stem = stem.strip("._-")
    return stem or "site"


def _company_name(metadata):
    """Best-effort human name for the site."""
    domain = metadata.get("target_domain", "") or ""
    return (
        metadata.get("company_name")
        or metadata.get("name")
        or (domain.split(".")[0].title() if domain else "Website")
    )


def _link_label(url):
    """Derive a readable label from a URL path (slug -> Title Case)."""
    path = urlparse(url).path.strip("/")
    if not path:
        return "Home"
    slug = path.rstrip("/").split("/")[-1]
    slug = slug.split(".")[0]  # drop file extension if any
    label = slug.replace("-", " ").replace("_", " ").strip()
    return label.title() if label else path


def build_llms_txt(data):
    """Build the ``llms.txt`` contents (str) from collected analysis ``data``.

    Pure function of the loaded JSON so it can be unit-tested without I/O.
    """
    metadata = data.get("metadata", {})
    domain = metadata.get("target_domain", "")
    company = _company_name(metadata)

    sitemap = data.get("sitemap_analysis", {}).get(domain, {})
    sample_urls = sitemap.get("sample_urls", []) or []
    total_urls = sitemap.get("total_urls", 0)

    # Bucket sample URLs by their categorized type.
    buckets = {}
    for entry in sample_urls:
        url = entry.get("url")
        if not url:
            continue
        buckets.setdefault(entry.get("type", "other"), []).append(url)

    lines = []
    lines.append(f"# {company}")
    lines.append("")
    if domain:
        lines.append(
            f"> Canonical entry points for {domain}, generated from sitemap "
            f"analysis to help AI agents and LLM tools navigate the site."
        )
        lines.append("")

    # Key pages: homepage first, then static/other pages.
    # Every URL is validated because sitemap content is externally controlled.
    key_pages = []
    home_url = _safe_link_url(f"https://{domain}/") if domain else None
    if home_url:
        key_pages.append((home_url, "Home"))
    for url in buckets.get("static", []) + buckets.get("other", []):
        safe = _safe_link_url(url)
        if safe:
            key_pages.append((safe, _link_label(safe)))
    if key_pages:
        lines.append("## Key pages")
        for url, label in key_pages[:MAX_LINKS_PER_SECTION]:
            lines.append(f"- [{label}]({url})")
        lines.append("")

    # Categorized sections.
    for type_key, title in SECTION_ORDER:
        urls = [u for u in (_safe_link_url(x) for x in buckets.get(type_key, [])) if u]
        if not urls:
            continue
        lines.append(f"## {title}")
        for url in urls[:MAX_LINKS_PER_SECTION]:
            lines.append(f"- [{_link_label(url)}]({url})")
        lines.append("")

    # Notes / provenance + the explicit optionality disclaimer.
    generated = metadata.get("analysis_date") or datetime.now().isoformat()
    lines.append("## Notes")
    lines.append(
        f"- Generated by seo-aeo-geo-analyzer on {generated[:10]} from "
        f"{total_urls} sitemap URLs (top samples shown)."
    )
    lines.append(
        "- llms.txt is an optional, emerging convention (https://llmstxt.org). "
        "It is NOT required for Google Search and does not affect ranking."
    )
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    project_dir = get_current_project_path()
    analysis_file = get_latest_file("analysis_data_*.json", project_dir)

    if not analysis_file:
        print("ERROR: No analysis_data_*.json found. Run step 1 (collect_data) first.")
        raise SystemExit(1)

    with open(analysis_file) as f:
        data = json.load(f)

    content = build_llms_txt(data)

    domain = data.get("metadata", {}).get("target_domain", "site")
    # Confine the output strictly to the project directory (defense in depth
    # against a domain value containing path separators or traversal).
    filename = os.path.basename(f"{_safe_filename_stem(domain)}-llms.txt")
    output_file = os.path.join(project_dir, filename)
    with open(output_file, "w") as f:
        f.write(content)

    print(f"\n✓ Generated recommended llms.txt for {domain}")
    print(f"✓ Saved to {output_file}")
    print("\nℹ llms.txt is optional and not a Google Search requirement.")
    print(f"  To use it, host the file at https://{domain}/llms.txt")


if __name__ == "__main__":
    main()
