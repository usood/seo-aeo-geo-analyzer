#!/usr/bin/env python3
"""
Configuration Loader for SEO Gap Analyzer
Loads and validates YAML configuration files
"""

import yaml
import os
import sys
from typing import Dict, List, Optional

class Config:
    """Configuration manager for SEO Gap Analyzer"""

    def __init__(self, config_path: str = "config.yaml"):
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found: {config_path}")
            print(f"Copy config.example.yaml to {config_path} and customize it.")
            sys.exit(1)

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self._validate()

    def _validate(self):
        """Validate required configuration fields"""
        required_fields = [
            ('target', 'domain'),
            ('target', 'name'),
            ('competitors',),
            ('location', 'country'),
            ('location', 'language_code'),
        ]

        for field_path in required_fields:
            current = self.config
            for key in field_path:
                if key not in current:
                    print(f"ERROR: Missing required configuration: {' -> '.join(field_path)}")
                    sys.exit(1)
                current = current[key]

        # Validate competitors format
        if not isinstance(self.config['competitors'], list):
            print("ERROR: 'competitors' must be a list")
            sys.exit(1)

        if len(self.config['competitors']) == 0:
            print("ERROR: At least one competitor must be specified")
            sys.exit(1)

    @property
    def target_domain(self) -> str:
        """Get target domain"""
        return self.config['target']['domain']

    @property
    def target_name(self) -> str:
        """Get target name"""
        return self.config['target']['name']

    @property
    def industry(self) -> str:
        """Get industry"""
        return self.config['target'].get('industry', 'E-commerce')

    @property
    def competitors(self) -> Dict[str, str]:
        """Get competitors as dict {domain: name}"""
        return {
            comp['domain']: comp['name']
            for comp in self.config['competitors']
        }

    @property
    def location_country(self) -> str:
        """Get location country"""
        return self.config['location']['country']

    @property
    def language_code(self) -> str:
        """Get language code"""
        return self.config['location']['language_code']

    @property
    def primary_color(self) -> str:
        """Get primary brand color"""
        return self.config.get('branding', {}).get('primary_color', '#3b82f6')

    @property
    def primary_dark(self) -> str:
        """Get dark primary color"""
        return self.config.get('branding', {}).get('primary_dark', '#2563eb')

    @property
    def accent_color(self) -> str:
        """Get accent color"""
        return self.config.get('branding', {}).get('accent_color', '#10b981')

    @property
    def logo_emoji(self) -> str:
        """Get logo emoji"""
        return self.config.get('branding', {}).get('logo_emoji', '🚀')

    @property
    def keywords_per_domain(self) -> int:
        """Get number of keywords to collect per domain"""
        return self.config.get('analysis', {}).get('keywords_per_domain', 100)

    @property
    def test_urls(self) -> Dict[str, str]:
        """Get test URLs for GEO analysis (auto-fills empty ones)"""
        urls = self.config.get('analysis', {}).get('test_urls', {})
        base_url = f"https://{self.target_domain}"

        defaults = {
            'homepage': base_url + '/',
            'product': '',
            'category': '',
            'blog': ''
        }

        return {key: urls.get(key) or defaults.get(key, '') for key in defaults.keys()}

    @property
    def performance_urls(self) -> List[str]:
        """Get performance test URLs (auto-fills if empty)"""
        urls = self.config.get('analysis', {}).get('performance_urls', [])
        # Filter out empty strings and use defaults if needed
        urls = [url for url in urls if url]

        if not urls:
            return [f"https://{self.target_domain}/"]

        return urls

    @property
    def seed_keywords(self) -> List[str]:
        """Get seed keywords"""
        return self.config.get('seed_keywords', [])

    @property
    def report_sections(self) -> List[str]:
        """Get included report sections"""
        return self.config.get('report', {}).get('include_sections', [
            'executive_summary',
            'sitemap_analysis',
            'social_presence',
            'keyword_gaps',
            'geo_optimization',
            'performance_audit',
            'recommendations'
        ])

    @property
    def company_name(self) -> str:
        """Get company name for report"""
        return self.config.get('report', {}).get('company_name', self.target_name)

    @property
    def report_title(self) -> str:
        """Get report title"""
        return self.config.get('report', {}).get('report_title', 'SEO Gap Analysis')

    @property
    def author(self) -> str:
        """Get report author"""
        return self.config.get('report', {}).get('author', 'SEO Team')

    def get(self, *keys, default=None):
        """Get nested configuration value"""
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def __repr__(self):
        return f"Config(target={self.target_domain}, competitors={len(self.competitors)})"


# Convenience function
def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration from file"""
    return Config(config_path)


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        print("✓ Configuration loaded successfully")
        print(f"  Target: {config.target_name} ({config.target_domain})")
        print(f"  Competitors: {len(config.competitors)}")
        print(f"  Location: {config.location_country}")
        print(f"  Language: {config.language_code}")
        print(f"  Branding: {config.logo_emoji} {config.primary_color}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)
