#!/usr/bin/env python3
"""
Setup script for SEO Gap Analyzer
Helps users configure the tool for first-time use
"""

import os
import shutil
import sys

def setup():
    """Interactive setup process"""
    print("="*60)
    print("SEO GAP ANALYZER - SETUP")
    print("="*60)
    print()

    # Check if config.yaml exists
    if os.path.exists('config.yaml'):
        print("✓ config.yaml already exists")
        overwrite = input("  Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("  Keeping existing config.yaml")
        else:
            create_config()
    else:
        create_config()

    # Check if .env exists
    if os.path.exists('.env'):
        print("✓ .env already exists")
        overwrite = input("  Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("  Keeping existing .env")
        else:
            create_env()
    else:
        create_env()

    print()
    print("="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Edit config.yaml with your brand and competitor info")
    print("2. Edit .env with your DataForSEO API credentials")
    print("3. Run: python run_analysis.py")
    print()

def create_config():
    """Create config.yaml from example"""
    if os.path.exists('config.example.yaml'):
        shutil.copy('config.example.yaml', 'config.yaml')
        print("✓ Created config.yaml from config.example.yaml")
    else:
        print("✗ config.example.yaml not found!")
        sys.exit(1)

def create_env():
    """Create .env from example"""
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print("✓ Created .env from .env.example")
    else:
        print("✗ .env.example not found!")
        sys.exit(1)

if __name__ == "__main__":
    setup()
