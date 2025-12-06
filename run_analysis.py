#!/usr/bin/env python3
"""
Master Orchestrator Script for SEO Analysis
Interactive workflow manager for Unleash Wellness SEO audit
Date: December 5, 2025
"""

import subprocess
import sys
import os
import json
import glob
from datetime import datetime

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(step_num, text):
    """Print step number and description"""
    print(f"{Colors.CYAN}{Colors.BOLD}[Step {step_num}]{Colors.ENDC} {text}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['requests', 'beautifulsoup4', 'python-dotenv']
    missing = []

    for package in required_packages:
        try:
            __import__(package if package != 'beautifulsoup4' else 'bs4')
        except ImportError:
            missing.append(package)

    if missing:
        print_error(f"Missing required packages: {', '.join(missing)}")
        print_info(f"Install with: pip install {' '.join(missing)}")
        return False

    return True

def run_script(script_name, description):
    """Run a Python script and show output"""
    print_step("Running", description)
    print(f"{Colors.BOLD}Executing: {script_name}{Colors.ENDC}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=True
        )
        print_success(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with error code {e.returncode}")
        return False
    except FileNotFoundError:
        print_error(f"Script not found: {script_name}")
        return False

def find_latest_file(pattern):
    """Find the most recently created file matching pattern"""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def show_menu():
    """Show interactive menu"""
    print_header("UNLEASH WELLNESS SEO ANALYSIS WORKFLOW")

    print(f"{Colors.BOLD}Available Analysis Steps:{Colors.ENDC}\n")

    steps = [
        ("1", "Sitemap & Social Analysis", "collect_data.py", "~30 seconds"),
        ("2", "DataForSEO API Collection", "dataforseo_collection.py", "~20-30 minutes, ~$6.45"),
        ("3", "GEO (JSON-LD) Analysis", "geo_analyzer.py", "~30 seconds"),
        ("4", "Google Data (GSC & GA4)", "google_integration.py", "~10 seconds"),
        ("5", "Performance Analysis", "performance_check.py", "~2-3 minutes"),
        ("6", "Generate HTML Report", "generate_report.py", "~5 seconds"),
        ("7", "Export Data (CSV/Excel/PDF)", "export_data.py", "~10 seconds"),
        ("A", "Run ALL Steps (Complete Analysis)", "", "~25-35 minutes total"),
        ("Q", "Quit", "", "")
    ]

    for num, desc, script, time in steps:
        if num == "Q":
            print(f"\n{Colors.YELLOW}{num}.{Colors.ENDC} {desc}")
        elif num == "A":
            print(f"\n{Colors.GREEN}{Colors.BOLD}{num}.{Colors.ENDC} {Colors.BOLD}{desc}{Colors.ENDC} {Colors.CYAN}({time}){Colors.ENDC}")
        else:
            print(f"{num}. {desc}")
            print(f"   {Colors.CYAN}Script: {script} | Time: {time}{Colors.ENDC}")

    print()

def check_prerequisites(step):
    """Check if prerequisites for a step are met"""
    if step == "6":  # Generate report needs data files
        # Check for dataforseo data
        dataforseo_file = find_latest_file("dataforseo_final_*.json")
        if not dataforseo_file:
            print_warning("DataForSEO data not found. Run step 2 first.")
            return False

        # Check for sitemap data
        sitemap_file = find_latest_file("analysis_data_*.json")
        if not sitemap_file:
            print_warning("Sitemap data not found. Run step 1 first.")
            return False

        # Check for GEO data
        if not os.path.exists("geo_analysis.json"):
            print_warning("GEO analysis data not found. Run step 3 first.")
            return False

        # Check for performance data
        if not os.path.exists("performance_analysis.json"):
            print_warning("Performance data not found. Run step 5 first.")
            return False

    return True

def run_all_steps():
    """Run complete workflow"""
    print_header("RUNNING COMPLETE ANALYSIS WORKFLOW")

    steps = [
        ("collect_data.py", "Sitemap & Social Analysis"),
        ("dataforseo_collection.py", "DataForSEO API Collection (This will take 20-30 minutes)"),
        ("geo_analyzer.py", "GEO JSON-LD Analysis"),
        ("google_integration.py", "Google Data Integration"),
        ("performance_check.py", "Performance Analysis"),
        ("generate_report.py", "HTML Report Generation")
    ]

    results = []

    for i, (script, description) in enumerate(steps, 1):
        print(f"\n{Colors.BOLD}Progress: {i}/{len(steps)}{Colors.ENDC}")

        if not os.path.exists(script):
            print_error(f"Script not found: {script}")
            if script == "generate_report.py":
                print_warning("Report generator script needs to be created first")
            results.append((description, False))
            continue

        success = run_script(script, description)
        results.append((description, success))

        if not success:
            print_error(f"Step {i} failed. Stopping workflow.")
            break

    # Show summary
    print_header("WORKFLOW SUMMARY")

    all_success = all(success for _, success in results)

    for description, success in results:
        if success:
            print_success(description)
        else:
            print_error(description)

    if all_success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All steps completed successfully!{Colors.ENDC}")

        # Find and display report location
        report_file = find_latest_file("unleash-wellness-seo-audit-*.html")
        if report_file:
            print_info(f"Report saved to: {report_file}")
            print_info(f"Open with: open {report_file}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some steps failed. Please review errors above.{Colors.ENDC}")

def show_status():
    """Show status of existing data files"""
    print_header("DATA FILES STATUS")

    files_to_check = [
        ("analysis_data_*.json", "Sitemap & Social Data", "Step 1"),
        ("dataforseo_final_*.json", "DataForSEO Complete Data", "Step 2"),
        ("geo_analysis.json", "GEO Analysis", "Step 3"),
        ("performance_analysis.json", "Performance Data", "Step 4"),
        ("unleash-wellness-seo-audit-*.html", "HTML Report", "Step 5")
    ]

    for pattern, description, step in files_to_check:
        if '*' in pattern:
            latest = find_latest_file(pattern)
            if latest:
                mod_time = datetime.fromtimestamp(os.path.getmtime(latest))
                print_success(f"{description}: {os.path.basename(latest)}")
                print(f"          Created: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print_warning(f"{description}: Not found (Run {step})")
        else:
            if os.path.exists(pattern):
                mod_time = datetime.fromtimestamp(os.path.getmtime(pattern))
                print_success(f"{description}: {pattern}")
                print(f"          Created: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print_warning(f"{description}: Not found (Run {step})")

    print()

def main():
    """Main orchestrator function"""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    while True:
        show_menu()

        # Show status
        print(f"{Colors.BOLD}Current Status:{Colors.ENDC}")
        show_status()

        choice = input(f"{Colors.BOLD}Select option: {Colors.ENDC}").strip().upper()

        if choice == "Q":
            print(f"\n{Colors.CYAN}Goodbye!{Colors.ENDC}")
            break

        elif choice == "A":
            confirm = input(f"\n{Colors.YELLOW}This will run all steps (~25-35 minutes, ~$6.45 cost). Continue? (y/N): {Colors.ENDC}").strip().lower()
            if confirm == 'y':
                run_all_steps()
            else:
                print_info("Cancelled.")

        elif choice == "1":
            run_script("collect_data.py", "Sitemap & Social Analysis")

        elif choice == "2":
            confirm = input(f"\n{Colors.YELLOW}This will run DataForSEO API calls (~$6.45 cost). Continue? (y/N): {Colors.ENDC}").strip().lower()
            if confirm == 'y':
                run_script("dataforseo_collection.py", "DataForSEO API Collection")
            else:
                print_info("Cancelled.")

        elif choice == "3":
            run_script("geo_analyzer.py", "GEO JSON-LD Analysis")

        elif choice == "4":
            run_script("google_integration.py", "Google Data Integration")

        elif choice == "5":
            run_script("performance_check.py", "Performance Analysis")

        elif choice == "6":
            if check_prerequisites("6"):
                if os.path.exists("generate_report.py"):
                    run_script("generate_report.py", "HTML Report Generation")
                else:
                    print_error("Report generator script not found!")
                    print_info("The report generator needs to be created from analyze_and_generate_report.py")
            else:
                print_error("Prerequisites not met. Please run required steps first.")

        elif choice == "7":
            run_script("export_data.py", "Export Data to CSV/Excel/PDF")

        else:
            print_error("Invalid option. Please try again.")

        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
        print("\n" * 2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user. Exiting...{Colors.ENDC}")
        sys.exit(0)
