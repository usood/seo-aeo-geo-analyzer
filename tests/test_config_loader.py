#!/usr/bin/env python3
"""
Tests for config_loader.py
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import Config


class TestConfigLoader:
    """Test configuration loading and validation"""

    def test_load_example_config(self):
        """Test loading the example configuration"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.target_domain == "allbirds.com"
        assert config.target_name == "Allbirds"
        assert config.industry == "DTC E-commerce - Footwear"

    def test_competitors(self):
        """Test competitor loading"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        competitors = config.competitors
        assert len(competitors) == 4
        assert "rothys.com" in competitors
        assert competitors["rothys.com"] == "Rothy's"

    def test_location_settings(self):
        """Test location and language settings"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.location_country == "United States"
        assert config.language_code == "en"

    def test_branding(self):
        """Test branding configuration"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.primary_color == "#111827"
        assert config.primary_dark == "#030712"
        assert config.logo_emoji == "👟"

    def test_analysis_settings(self):
        """Test analysis configuration"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.keywords_per_domain == 100
        assert len(config.seed_keywords) == 3
        assert "sustainable shoes" in config.seed_keywords

    def test_test_urls(self):
        """Test URL configuration"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        urls = config.test_urls
        assert urls['homepage'] == "https://allbirds.com/"
        assert urls['product'] == "https://www.allbirds.com/products/mens-tree-runners"

    def test_performance_urls(self):
        """Test performance URLs"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        urls = config.performance_urls
        assert len(urls) == 3
        assert "https://www.allbirds.com/" in urls

    def test_report_settings(self):
        """Test report configuration"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.company_name == "Allbirds"
        assert config.report_title == "DTC SEO Gap Analysis"
        assert len(config.report_sections) == 7

    def test_missing_config_file(self):
        """Test handling of missing config file"""
        with pytest.raises(SystemExit):
            Config("nonexistent.yaml")

    def test_saas_config(self):
        """Test B2B SaaS configuration example"""
        config = Config("examples/configs/saas-b2b.yaml")

        assert config.target_domain == "asana.com"
        assert config.industry == "B2B SaaS - Work Management"
        assert len(config.competitors) == 4

    def test_d2c_config(self):
        """Test D2C e-commerce configuration example"""
        config = Config("examples/configs/d2c-ecommerce.yaml")

        assert config.target_domain == "allbirds.com"
        assert config.industry == "DTC E-commerce - Footwear"
        assert config.logo_emoji == "👟"

    def test_consumer_app_config(self):
        """Test consumer app configuration example"""
        config = Config("examples/configs/consumer-app.yaml")

        assert config.target_domain == "duolingo.com"
        assert config.industry == "Consumer App - Education"
        assert len(config.competitors) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
