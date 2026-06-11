#!/usr/bin/env python3
"""
Lighthouse agentic-browsing readiness check.

Chrome ships an experimental Lighthouse "agentic-browsing" category that reports
how ready a page is for AI agents (WebMCP tool registration, agent-centric
accessibility, layout stability, root llms.txt presence, etc.). It is only
available in recent local Lighthouse runtimes.

This script runs the *local* Lighthouse CLI for that category when available and
falls back cleanly when it is not (Lighthouse not installed, Chrome missing, or
the category unsupported by the installed version). Results are written to
``agentic_browsing.json`` and surfaced in the HTML report.

The category is experimental; treat results as engineering readiness signals,
not a confirmed search ranking factor.

Date: December 7, 2025
"""

import json
import os
import shutil
import subprocess
from urllib.parse import urlparse

from utils.path_manager import get_current_project_path, get_latest_file

CATEGORY_ID = "agentic-browsing"
RUN_TIMEOUT_SECONDS = 180


def find_lighthouse(which=shutil.which):
    """Return a command prefix list to invoke Lighthouse, or None if absent.

    Prefers a directly installed ``lighthouse`` binary, then ``npx lighthouse``.
    """
    if which("lighthouse"):
        return ["lighthouse"]
    if which("npx"):
        return ["npx", "--no-install", "lighthouse"]
    return None


def _valid_target(url):
    """Only allow http(s) URLs with a host.

    This also prevents argument injection: a validated URL cannot begin with
    ``-`` / ``--`` and so can't be misread as a Lighthouse flag.
    """
    if not url:
        return False
    parsed = urlparse(str(url))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_agentic_result(lhr):
    """Extract the agentic-browsing category from a Lighthouse result (lhr).

    Pure function. Returns a dict with ``available`` plus, when present, the
    category score and a compact list of audit signals.
    """
    categories = (lhr or {}).get("categories", {})
    category = categories.get(CATEGORY_ID)
    if not category:
        return {
            "available": False,
            "reason": "The installed Lighthouse runtime does not expose the "
            "'agentic-browsing' category (it is experimental and version-gated).",
        }

    audits = (lhr or {}).get("audits", {})
    signals = []
    for ref in category.get("auditRefs", []):
        audit = audits.get(ref.get("id"), {})
        if not audit:
            continue
        signals.append({
            "id": ref.get("id"),
            "title": audit.get("title"),
            "score": audit.get("score"),
            "scoreDisplayMode": audit.get("scoreDisplayMode"),
            "displayValue": audit.get("displayValue"),
        })

    return {
        "available": True,
        "category_title": category.get("title", "Agentic Browsing"),
        "score": category.get("score"),  # often None: fractional/pass-fail signals
        "lighthouse_version": (lhr or {}).get("lighthouseVersion"),
        "signals": signals,
    }


def run_agentic_check(url, run=subprocess.run, which=shutil.which):
    """Run the local Lighthouse agentic-browsing audit for ``url``.

    Dependency-injected (``run``/``which``) for testing. Always returns a dict;
    never raises for the expected "not available" conditions.
    """
    result = {"url": url}

    if not _valid_target(url):
        result.update(available=False, reason="No valid http(s) target URL to audit.")
        return result

    prefix = find_lighthouse(which)
    if not prefix:
        result.update(
            available=False,
            reason="Lighthouse CLI not found. Install it (npm i -g lighthouse) "
            "to enable agentic-browsing checks.",
        )
        return result

    cmd = prefix + [
        url,
        f"--only-categories={CATEGORY_ID}",
        "--output=json",
        "--output-path=stdout",
        "--quiet",
        "--chrome-flags=--headless=new --no-sandbox",
    ]

    try:
        proc = run(cmd, capture_output=True, text=True, timeout=RUN_TIMEOUT_SECONDS)
    except FileNotFoundError:
        result.update(available=False, reason="Lighthouse executable could not be launched.")
        return result
    except subprocess.TimeoutExpired:
        result.update(available=False, reason=f"Lighthouse timed out after {RUN_TIMEOUT_SECONDS}s.")
        return result
    except Exception as exc:  # defensive: never crash the optional step
        result.update(available=False, reason=f"Lighthouse failed to run: {exc}")
        return result

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip().splitlines()
        detail = stderr[-1] if stderr else "unknown error"
        result.update(
            available=False,
            reason=f"Lighthouse exited with code {proc.returncode}: {detail}",
        )
        return result

    try:
        lhr = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        result.update(available=False, reason="Could not parse Lighthouse JSON output.")
        return result

    result.update(parse_agentic_result(lhr))
    return result


def _target_url(data):
    """Homepage of the analyzed site from collected metadata."""
    domain = (data.get("metadata", {}) or {}).get("target_domain", "")
    return f"https://{domain}/" if domain else ""


def main():
    project_dir = get_current_project_path()
    analysis_file = get_latest_file("analysis_data_*.json", project_dir)

    data = {}
    if analysis_file:
        with open(analysis_file) as f:
            data = json.load(f)

    url = _target_url(data)
    result = run_agentic_check(url)

    output_file = os.path.join(project_dir, "agentic_browsing.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    if result.get("available"):
        print(f"\n✓ Agentic-browsing audit complete for {url}")
        score = result.get("score")
        print(f"  Category score: {score if score is not None else 'n/a (pass/fail signals)'}")
    else:
        print(f"\nℹ Agentic-browsing category not run: {result.get('reason')}")
        print("  This is expected when the local Lighthouse runtime lacks the category.")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    main()
