"""Tests for generate_site_llms.build_llms_txt."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generate_site_llms import (
    build_llms_txt,
    _link_label,
    _safe_link_url,
    _safe_filename_stem,
)


SAMPLE = {
    "metadata": {
        "target_domain": "example-shop.com",
        "company_name": "Example Shop",
        "analysis_date": "2025-12-07T10:00:00",
    },
    "sitemap_analysis": {
        "example-shop.com": {
            "total_urls": 120,
            "sample_urls": [
                {"url": "https://example-shop.com/products/blue-widget", "type": "product"},
                {"url": "https://example-shop.com/products/red-widget", "type": "product"},
                {"url": "https://example-shop.com/collections/widgets", "type": "category"},
                {"url": "https://example-shop.com/blogs/how-to-widget", "type": "content"},
                {"url": "https://example-shop.com/about", "type": "static"},
            ],
        }
    },
}


class BuildLlmsTxtTest(unittest.TestCase):
    def setUp(self):
        self.out = build_llms_txt(SAMPLE)

    def test_starts_with_company_title(self):
        self.assertTrue(self.out.startswith("# Example Shop"))

    def test_homepage_is_a_key_page(self):
        self.assertIn("## Key pages", self.out)
        self.assertIn("[Home](https://example-shop.com/)", self.out)

    def test_categorized_sections_present(self):
        self.assertIn("## Products & services", self.out)
        self.assertIn("## Categories", self.out)
        self.assertIn("## Content & resources", self.out)

    def test_product_links_rendered(self):
        self.assertIn("(https://example-shop.com/products/blue-widget)", self.out)

    def test_includes_optionality_disclaimer(self):
        self.assertIn("NOT required for Google Search", self.out)

    def test_reports_total_url_count(self):
        self.assertIn("120 sitemap URLs", self.out)

    def test_ends_with_single_trailing_newline(self):
        self.assertTrue(self.out.endswith("\n"))
        self.assertFalse(self.out.endswith("\n\n"))

    def test_label_from_slug(self):
        self.assertEqual(_link_label("https://x.com/products/blue-widget"), "Blue Widget")
        self.assertEqual(_link_label("https://x.com/"), "Home")

    def test_empty_data_does_not_crash(self):
        out = build_llms_txt({})
        self.assertIn("# Website", out)
        self.assertIn("## Notes", out)


class SecurityHardeningTest(unittest.TestCase):
    def test_safe_link_url_accepts_http_and_https(self):
        self.assertEqual(_safe_link_url("https://x.com/a"), "https://x.com/a")
        self.assertEqual(_safe_link_url("http://x.com/a"), "http://x.com/a")

    def test_safe_link_url_rejects_dangerous_schemes(self):
        self.assertIsNone(_safe_link_url("javascript:alert(1)"))
        self.assertIsNone(_safe_link_url("data:text/html,evil"))
        self.assertIsNone(_safe_link_url("file:///etc/passwd"))

    def test_safe_link_url_rejects_control_chars_and_markdown_breakers(self):
        self.assertIsNone(_safe_link_url("https://x.com/a\nb"))
        self.assertIsNone(_safe_link_url("https://x.com/a b"))
        self.assertIsNone(_safe_link_url("https://x.com/a(b)"))

    def test_malicious_sitemap_urls_excluded_from_output(self):
        data = {
            "metadata": {"target_domain": "x.com"},
            "sitemap_analysis": {
                "x.com": {
                    "total_urls": 2,
                    "sample_urls": [
                        {"url": "javascript:alert(1)", "type": "product"},
                        {"url": "https://x.com/products/ok", "type": "product"},
                    ],
                }
            },
        }
        out = build_llms_txt(data)
        self.assertNotIn("javascript:", out)
        self.assertIn("https://x.com/products/ok", out)

    def test_safe_filename_stem_strips_traversal(self):
        self.assertEqual(_safe_filename_stem("../../etc/passwd"), "etc_passwd")
        self.assertEqual(_safe_filename_stem("a/b/c"), "a_b_c")
        self.assertEqual(_safe_filename_stem("good-domain.com"), "good-domain.com")
        self.assertEqual(_safe_filename_stem(""), "site")
        # No path separator can survive, so os.path.join cannot escape.
        self.assertNotIn("/", _safe_filename_stem("../../x"))


if __name__ == "__main__":
    unittest.main()
