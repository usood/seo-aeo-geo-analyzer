#!/usr/bin/env python3
"""
Tests for URL categorization logic
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import categorize_url function from collect_data
import importlib.util
spec = importlib.util.spec_from_file_location("collect_data", "collect_data.py")
collect_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect_data)

categorize_url = collect_data.categorize_url


class TestURLCategorization:
    """Test URL categorization for different platforms"""

    def test_shopify_product_urls(self):
        """Test Shopify product URL detection"""
        urls = [
            "https://example.com/products/jolly-gut",
            "https://example.com/products/dog-vitamins",
            "https://example.com/products/pet-supplement-123"
        ]

        for url in urls:
            assert categorize_url(url) == 'product'

    def test_shopify_collection_urls(self):
        """Test Shopify collection URL detection"""
        urls = [
            "https://example.com/collections/all",
            "https://example.com/collections/supplements",
            "https://example.com/collections/dog-health"
        ]

        for url in urls:
            assert categorize_url(url) == 'category'

    def test_blog_urls(self):
        """Test blog/content URL detection"""
        urls = [
            "https://example.com/blogs/pet-wellness",
            "https://example.com/blogs/news/article-title",
            "https://example.com/articles/pet-care-tips"
        ]

        for url in urls:
            assert categorize_url(url) == 'content'

    def test_static_page_urls(self):
        """Test static page URL detection"""
        urls = [
            "https://example.com/pages/about",
            "https://example.com/pages/contact",
            "https://example.com/pages/faq"
        ]

        for url in urls:
            assert categorize_url(url) == 'static'

    def test_other_urls(self):
        """Test uncategorized URLs"""
        urls = [
            "https://example.com/",
            "https://example.com/search",
            "https://example.com/account/login"
        ]

        for url in urls:
            assert categorize_url(url) == 'other'

    def test_case_insensitivity(self):
        """Test that categorization is case-insensitive"""
        assert categorize_url("https://example.com/PRODUCTS/test") == 'product'
        assert categorize_url("https://example.com/Collections/all") == 'category'
        assert categorize_url("https://example.com/BLOGS/post") == 'content'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
