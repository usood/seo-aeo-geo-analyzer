#!/usr/bin/env python3
"""
Tests for config_loader.py
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_loader import Config


class TestConfigLoader:
    """Test configuration loading and validation"""

    def test_load_example_config(self):
        """Test loading the example configuration"""
        config = Config("examples/configs/unleash-wellness.yaml")

        assert config.target_domain == "unleashwellness.co"
        assert config.target_name == "Unleash Wellness"
        assert config.industry == "Pet Wellness E-commerce"

    def test_competitors(self):
        """Test competitor loading"""
        config = Config("examples/configs/unleash-wellness.yaml")

        competitors = config.competitors
        assert len(competitors) == 4
        assert "k9vitality.in" in competitors
        assert competitors["k9vitality.in"] == "K9 Vitality"

    def test_location_settings(self):
        """Test location and language settings"""
        config = Config("examples/configs/unleash-wellness.yaml")

        assert config.location_country == "India"
        assert config.language_code == "en"

    def test_branding(self):
        """Test branding configuration"""
        config = Config("examples/configs/unleash-wellness.yaml")

        assert config.primary_color == "#f59e0b"
        assert config.primary_dark == "#d97706"
        assert config.logo_emoji == "🐾"

    def test_analysis_settings(self):
        """Test analysis configuration"""
        config = Config("examples/configs/unleash-wellness.yaml")

        assert config.keywords_per_domain == 100
        assert len(config.seed_keywords) == 3
        assert "dog supplements" in config.seed_keywords

    def test_test_urls(self):
        """Test URL configuration"""
        config = Config("examples/configs/unleash-wellness.yaml")

        urls = config.test_urls
        assert urls['homepage'] == "https://unleashwellness.co/"
        assert urls['product'] == "https://unleashwellness.co/products/jolly-gut"

    def test_performance_urls(self):
        """Test performance URLs"""
        config = Config("examples/configs/unleash-wellness.yaml")

        urls = config.performance_urls
        assert len(urls) == 3
        assert "https://unleashwellness.co/" in urls

    def test_report_settings(self):
        """Test report configuration"""
        config = Config("examples/configs/unleash-wellness.yaml")

        assert config.company_name == "Unleash Wellness"
        assert config.report_title == "SEO Gap Analysis Report"
        assert len(config.report_sections) == 7

    def test_missing_config_file(self):
        """Test handling of missing config file"""
        with pytest.raises(SystemExit):
            Config("nonexistent.yaml")

    def test_saas_config(self):
        """Test B2B SaaS configuration example"""
        config = Config("examples/configs/saas-b2b.yaml")

        assert config.target_domain == "yourcompany.com"
        assert config.industry == "B2B SaaS - Project Management"
        assert len(config.competitors) == 4

    def test_d2c_config(self):
        """Test D2C e-commerce configuration example"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.target_domain == "yourbrand.com"
        assert config.industry == "D2C E-commerce - Fashion"
        assert config.logo_emoji == "👗"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
