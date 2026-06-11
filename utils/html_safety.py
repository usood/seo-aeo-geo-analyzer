"""Small escaping helpers for generated HTML reports."""

import re
import json
from html import escape
from urllib.parse import urlparse


def escape_html(value):
    """Escape untrusted text for HTML text or attribute contexts."""
    if value is None:
        return ""
    return escape(str(value), quote=True)


def safe_http_url(value):
    """Return an escaped HTTP(S) URL, or an empty string for unsafe schemes."""
    if not value:
        return ""

    url = str(value).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""

    return escape_html(url)


def safe_css_class(value):
    """Normalize untrusted values before interpolating into class attributes."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "").lower())


def json_script_value(value):
    """Encode a value for JSON embedded in an HTML script tag."""
    return json.dumps(str(value or "")).replace("</", "<\\/")
