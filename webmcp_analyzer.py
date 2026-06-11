#!/usr/bin/env python3
"""
WebMCP opportunity analyzer.

WebMCP is a proposed Chrome standard for exposing structured browser *tools* to
AI agents, so an agent can reliably perform actions (checkout, booking, form
submission, search, account/support flows) instead of guessing at the DOM.

This module flags action-oriented pages on the analyzed site and produces a
WebMCP *opportunity* score, so teams can see where exposing agent tools would
add the most value. It is heuristic and offline (no API cost): it reasons over
the sitemap sample collected by ``collect_data.py`` plus detected technology.

Caveats surfaced in the output:
- WebMCP is experimental / proposed; treat this as a readiness signal.
- Action pages (checkout, login, cart) are frequently excluded from sitemaps,
  so a low count is a floor, not a ceiling, on real opportunity.

Date: December 7, 2025
"""

import json
import os

from utils.path_manager import get_current_project_path, get_latest_file

# Action categories: (label, weight, url substrings). Weight reflects how much
# agent tooling typically helps that flow. Presence (not count) drives scoring.
ACTION_SIGNALS = [
    ("Checkout & cart", 25, ["/checkout", "/cart", "/basket", "/bag"]),
    ("Signup & onboarding", 20, [
        "/signup", "/sign-up", "/register", "/join", "/get-started",
        "/start", "/trial", "/free-trial",
    ]),
    ("Booking & scheduling", 20, [
        "/book", "/booking", "/reserve", "/reservation", "/appointment",
        "/schedule",
    ]),
    ("Lead & enquiry forms", 18, [
        "/contact", "/demo", "/quote", "/request", "/apply", "/enquir",
        "/inquir", "/get-a-quote",
    ]),
    ("Account & dashboard", 12, [
        "/login", "/sign-in", "/signin", "/account", "/my-account",
        "/dashboard", "/portal",
    ]),
    ("Search & filtering", 10, ["/search", "/find", "/explore", "?q=", "&q="]),
    ("Support & help", 10, ["/support", "/help", "/ticket", "/chat"]),
]

# Technology fingerprints that imply commerce flows usually absent from sitemaps.
ECOMMERCE_TECH = ["shopify", "woocommerce", "magento", "bigcommerce", "prestashop", "salesforce commerce"]


def _matched_categories(url):
    """Return the list of action category labels a URL matches."""
    low = str(url or "").lower()
    matches = []
    for label, _weight, needles in ACTION_SIGNALS:
        if any(n in low for n in needles):
            matches.append(label)
    return matches


def _weight_for(label):
    for lbl, weight, _ in ACTION_SIGNALS:
        if lbl == label:
            return weight
    return 0


def analyze_webmcp(data):
    """Analyze collected ``data`` for WebMCP opportunity. Pure + testable.

    Returns a dict: score (0-100), level, flagged_pages, present_categories,
    inferred_flows, notes.
    """
    metadata = data.get("metadata", {})
    domain = metadata.get("target_domain", "")
    technology = str(metadata.get("technology", "") or "").lower()

    sitemap = data.get("sitemap_analysis", {}).get(domain, {})
    sample_urls = sitemap.get("sample_urls", []) or []

    flagged_pages = []
    present = set()
    for entry in sample_urls:
        url = entry.get("url")
        if not url:
            continue
        cats = _matched_categories(url)
        if cats:
            flagged_pages.append({"url": url, "categories": cats})
            present.update(cats)

    # Flows inferred from technology even when the pages aren't in the sitemap.
    inferred_flows = []
    if any(t in technology for t in ECOMMERCE_TECH):
        inferred_flows.append(
            "Commerce platform detected — checkout/cart and account flows almost "
            "certainly exist even if absent from the sitemap."
        )
        present.add("Checkout & cart")

    # Score = summed weights of distinct present categories, capped at 100.
    score = min(100, sum(_weight_for(c) for c in present))

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    elif score > 0:
        level = "Low"
    else:
        level = "None detected"

    notes = [
        "WebMCP is an experimental, proposed Chrome capability. Treat this as a "
        "readiness signal, not a ranking factor.",
        "Detection is heuristic, based on the sitemap sample and detected "
        "technology. Action pages (checkout, login, cart) are often excluded "
        "from sitemaps, so this score is a floor on real opportunity.",
    ]
    if level in ("High", "Medium"):
        notes.append(
            "Prioritize exposing WebMCP tools for the highest-weight flows above, "
            "keeping the human-facing UI fully functional as a progressive "
            "enhancement, and requiring visible confirmation for sensitive actions."
        )

    return {
        "domain": domain,
        "score": score,
        "level": level,
        "present_categories": sorted(present),
        "flagged_pages": flagged_pages,
        "inferred_flows": inferred_flows,
        "notes": notes,
    }


def main():
    project_dir = get_current_project_path()
    analysis_file = get_latest_file("analysis_data_*.json", project_dir)

    if not analysis_file:
        print("ERROR: No analysis_data_*.json found. Run step 1 (collect_data) first.")
        raise SystemExit(1)

    with open(analysis_file) as f:
        data = json.load(f)

    result = analyze_webmcp(data)

    output_file = os.path.join(project_dir, "webmcp_analysis.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n✓ WebMCP opportunity: {result['level']} (score {result['score']}/100)")
    if result["present_categories"]:
        print("  Action flows found: " + ", ".join(result["present_categories"]))
    print(f"✓ Saved to {output_file}")
    print("\nℹ WebMCP is experimental/proposed; treat results as a readiness signal.")


if __name__ == "__main__":
    main()
