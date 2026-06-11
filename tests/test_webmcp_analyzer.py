"""Tests for webmcp_analyzer.analyze_webmcp."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from webmcp_analyzer import analyze_webmcp, _matched_categories


def _data(urls, technology=""):
    return {
        "metadata": {"target_domain": "shop.com", "technology": technology},
        "sitemap_analysis": {
            "shop.com": {"sample_urls": [{"url": u, "type": "other"} for u in urls]}
        },
    }


class MatchedCategoriesTest(unittest.TestCase):
    def test_checkout_detected(self):
        self.assertIn("Checkout & cart", _matched_categories("https://x.com/checkout"))

    def test_booking_detected(self):
        self.assertIn("Booking & scheduling", _matched_categories("https://x.com/book-now"))

    def test_non_action_page_matches_nothing(self):
        self.assertEqual(_matched_categories("https://x.com/about-us"), [])


class AnalyzeWebmcpTest(unittest.TestCase):
    def test_no_action_pages_scores_zero(self):
        result = analyze_webmcp(_data(["https://shop.com/about", "https://shop.com/blog/x"]))
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["level"], "None detected")
        self.assertEqual(result["flagged_pages"], [])

    def test_flags_action_pages(self):
        result = analyze_webmcp(_data([
            "https://shop.com/cart",
            "https://shop.com/contact",
            "https://shop.com/account/login",
        ]))
        self.assertGreater(result["score"], 0)
        self.assertIn("Checkout & cart", result["present_categories"])
        self.assertIn("Lead & enquiry forms", result["present_categories"])
        urls = [p["url"] for p in result["flagged_pages"]]
        self.assertIn("https://shop.com/cart", urls)

    def test_score_capped_at_100(self):
        result = analyze_webmcp(_data([
            "https://shop.com/checkout", "https://shop.com/signup",
            "https://shop.com/book", "https://shop.com/contact",
            "https://shop.com/login", "https://shop.com/search",
            "https://shop.com/support",
        ]))
        self.assertLessEqual(result["score"], 100)
        self.assertEqual(result["level"], "High")

    def test_technology_infers_commerce_flow(self):
        # No action URLs in the sitemap, but Shopify implies checkout exists.
        result = analyze_webmcp(_data(["https://shop.com/products/x"], technology="Shopify"))
        self.assertIn("Checkout & cart", result["present_categories"])
        self.assertTrue(result["inferred_flows"])
        self.assertGreater(result["score"], 0)

    def test_levels(self):
        low = analyze_webmcp(_data(["https://shop.com/search"]))  # weight 10
        self.assertEqual(low["level"], "Low")

    def test_always_includes_experimental_caveat(self):
        result = analyze_webmcp(_data(["https://shop.com/cart"]))
        joined = " ".join(result["notes"]).lower()
        self.assertIn("experimental", joined)

    def test_empty_data_safe(self):
        result = analyze_webmcp({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["flagged_pages"], [])


if __name__ == "__main__":
    unittest.main()
