#!/usr/bin/env python3
"""
Export Analysis Data to CSV, Excel, and PDF
For: Unleash Wellness SEO Audit
Date: December 6, 2025
"""

import json
import glob
import os
import pandas as pd
from datetime import datetime
from utils.path_manager import get_current_project_path, get_latest_file
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

def load_data():
    """Load data from latest JSON files"""
    data = {}
    project_dir = get_current_project_path()
    
    # Load Sitemap/Social data
    sitemap_file = get_latest_file("analysis_data_*.json", project_dir)
    if sitemap_file:
        with open(sitemap_file, 'r') as f:
            data['sitemap'] = json.load(f)
            print(f"✓ Loaded: {sitemap_file}")
            
    # Load DataForSEO data
    dfs_file = get_latest_file("dataforseo_final_*.json", project_dir)
    if dfs_file:
        with open(dfs_file, 'r') as f:
            data['seo'] = json.load(f)
            print(f"✓ Loaded: {dfs_file}")
            
    # Load Performance data
    perf_file = os.path.join(project_dir, "performance_analysis.json")
    if os.path.exists(perf_file):
        with open(perf_file, 'r') as f:
            data['performance'] = json.load(f)
            print(f"✓ Loaded: {perf_file}")
            
    return data

def prepare_dfs(data):
    """Prepare Pandas DataFrames"""
    dfs = {}
    
    # 1. Keyword Gaps
    if 'seo' in data and 'gaps' in data['seo']:
        gaps = data['seo']['gaps'].get('top_100', [])
        if gaps:
            gap_list = []
            for g in gaps:
                gap_list.append({
                    'Keyword': g.get('keyword'),
                    'Search Volume': g.get('search_volume'),
                    'Competitor': g.get('competitor'),
                    'Competitor Position': g.get('competitor_position'),
                    'Difficulty': g.get('difficulty', 0),
                    'Intent': g.get('intent', 'unknown')
                })
            dfs['Keyword Gaps'] = pd.DataFrame(gap_list)
            
    # 2. Ranked Keywords (Target)
    if 'seo' in data and 'ranked_keywords' in data['seo']:
        # Assuming target domain is the first key if structure matches
        target_domain = data['sitemap']['metadata']['target_domain']
        if target_domain in data['seo']['ranked_keywords']:
            ranked = data['seo']['ranked_keywords'][target_domain]
            rank_list = []
            for r in ranked:
                rank_list.append({
                    'Keyword': r.get('keyword_data', {}).get('keyword'),
                    'Position': r.get('ranked_serp_element', {}).get('serp_item', {}).get('rank_group'),
                    'Volume': r.get('keyword_data', {}).get('keyword_info', {}).get('search_volume'),
                    'URL': r.get('ranked_serp_element', {}).get('serp_item', {}).get('url')
                })
            dfs['Current Rankings'] = pd.DataFrame(rank_list)

    # 3. Performance
    if 'performance' in data:
        perf_list = []
        for p in data['performance']:
            perf_list.append({
                'URL': p.get('url'),
                'Device': p.get('device'),
                'Score': p.get('performance_score'),
                'LCP': p.get('lcp'),
                'FID': p.get('fid'),
                'CLS': p.get('cls')
            })
        dfs['Performance'] = pd.DataFrame(perf_list)
        
    return dfs

def export_to_csv(dfs, output_dir):
    """Export DataFrames to CSV"""
    project_export_dir = os.path.join(get_current_project_path(), output_dir)
    os.makedirs(project_export_dir, exist_ok=True)
    for name, df in dfs.items():
        filename = os.path.join(project_export_dir, f"{name.lower().replace(' ', '_')}.csv")
        df.to_csv(filename, index=False)
        print(f"✓ Exported CSV: {filename}")

def export_to_excel(dfs, output_dir):
    """Export DataFrames to Excel"""
    project_export_dir = os.path.join(get_current_project_path(), output_dir)
    os.makedirs(project_export_dir, exist_ok=True)
    filename = os.path.join(project_export_dir, "seo_analysis_data.xlsx")
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for name, df in dfs.items():
                df.to_excel(writer, sheet_name=name[:31], index=False) # Excel sheet name limit
        print(f"✓ Exported Excel: {filename}")
    except Exception as e:
        print(f"⚠ Excel export failed: {e}")

class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'SEO Analysis Data Export', 0, 1, 'C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
else:
    class PDF: pass

def export_to_pdf(dfs, output_dir):
    """Export Data Summaries to PDF"""
    if not HAS_FPDF:
        print("⚠ PDF export skipped: 'fpdf' library not installed.")
        return

    project_export_dir = os.path.join(get_current_project_path(), output_dir)
    os.makedirs(project_export_dir, exist_ok=True)
    filename = os.path.join(project_export_dir, "seo_data_summary.pdf")
    
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        for name, df in dfs.items():
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Table: {name}", 0, 1)
            pdf.set_font("Arial", size=8)
            
            # Headers
            cols = df.columns.tolist()
            col_width = 190 / len(cols)
            for col in cols:
                pdf.cell(col_width, 7, str(col)[:20], 1)
            pdf.ln()
            
            # Rows (Limit to first 50 to avoid huge PDFs)
            for i, row in df.head(50).iterrows():
                for col in cols:
                    data_str = str(row[col])[:20] # Truncate
                    pdf.cell(col_width, 6, data_str, 1)
                pdf.ln()
            
            pdf.ln(10)
            
        pdf.output(filename)
        print(f"✓ Exported PDF: {filename}")
    except Exception as e:
        print(f"⚠ PDF export failed: {e}")

def main():
    print("="*60)
    print("EXPORTING ANALYSIS DATA")
    print("="*60)
    
    # Create output directory
    output_dir = "exports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Load and Prepare
    data = load_data()
    if not data:
        print("❌ No data found to export. Run analysis steps first.")
        return
        
    dfs = prepare_dfs(data)
    if not dfs:
        print("❌ No tabular data extracted.")
        return
        
    # Export
    print("\nExporting to formats...")
    export_to_csv(dfs, output_dir)
    export_to_excel(dfs, output_dir)
    export_to_pdf(dfs, output_dir)
    
    print(f"\n✅ Export complete! Check the '{output_dir}' folder.")

if __name__ == "__main__":
    main()
