#!/usr/bin/env python3
"""Tests for HTML report escaping helpers."""

from utils.html_safety import escape_html, json_script_value, safe_css_class, safe_http_url


def test_escape_html_escapes_scriptable_text():
    assert escape_html('<img src=x onerror="alert(1)">') == "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;"


def test_safe_http_url_allows_http_and_https():
    assert safe_http_url("https://example.com/logo.png") == "https://example.com/logo.png"
    assert safe_http_url("http://example.com/logo.png") == "http://example.com/logo.png"


def test_safe_http_url_rejects_script_urls():
    assert safe_http_url("javascript:alert(1)") == ""
    assert safe_http_url("data:text/html,<svg>") == ""


def test_safe_css_class_removes_unsafe_characters():
    assert safe_css_class('commercial" onclick="alert(1)') == "commercial-onclick-alert-1-"


def test_json_script_value_prevents_script_breakout():
    assert json_script_value("</script><script>alert(1)</script>") == '"<\\/script><script>alert(1)<\\/script>"'
