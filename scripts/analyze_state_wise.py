#!/usr/bin/env python3
"""
Detailed Analysis of State-Wise Tourism Spreadsheets (32 States / UTs)
Generates comprehensive report on 4,143 destination records, schema coverage,
category breakdown, ratings, and state-level statistics.
"""

import os
import glob
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(ROOT_DIR, "data", "raw", "extracted", "state_wise_tourism", "state-wise Dataset")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

def analyze_state_wise_data():
    files = sorted(glob.glob(os.path.join(STATE_DIR, "*.xlsx")))
    print(f"Analyzing {len(files)} state-wise Excel spreadsheets...")
    
    state_summaries = []
    category_counter = {}
    
    total_records = 0
    total_reviews = 0
    
    for f in files:
        file_basename = os.path.basename(f)
        state_name = file_basename.replace(".xlsx", "").title()
        
        df = pd.read_excel(f)
        row_cnt = len(df)
        col_cnt = len(df.columns)
        total_records += row_cnt
        
        # Check rating & review stats
        avg_score = df['totalScore'].mean() if 'totalScore' in df.columns else 0.0
        review_cnt = df['reviewsCount'].sum() if 'reviewsCount' in df.columns else 0
        total_reviews += review_cnt
        
        # Categories
        cat_sample = []
        if 'categoryName' in df.columns:
            cats = df['categoryName'].dropna().value_counts()
            cat_sample = list(cats.index[:3])
            for c, count in cats.items():
                category_counter[c] = category_counter.get(c, 0) + count
                
        # Sample destinations
        dest_sample = []
        if 'title' in df.columns:
            dest_sample = [str(x) for x in df['title'].dropna().tolist()[:3]]

        state_summaries.append({
            "state_ut": state_name,
            "filename": file_basename,
            "total_destinations": row_cnt,
            "columns": col_cnt,
            "avg_rating": round(avg_score, 2) if not np.isnan(avg_score) else "N/A",
            "total_reviews": int(review_cnt) if not np.isnan(review_cnt) else 0,
            "top_categories": ", ".join(cat_sample) if cat_sample else "N/A",
            "sample_places": ", ".join(dest_sample) if dest_sample else "N/A"
        })
        
    df_state = pd.DataFrame(state_summaries)
    
    # Save CSV summary
    csv_out = os.path.join(REPORTS_DIR, "state_wise_tourism_summary.csv")
    df_state.to_csv(csv_out, index=False)
    print(f"✓ Saved state-wise CSV summary to: {csv_out}")
    
    # Save Markdown report
    md_out = os.path.join(REPORTS_DIR, "state_wise_tourism_report.md")
    with open(md_out, "w") as mdf:
        mdf.write("# Detailed State-Wise Tourism Dataset Audit Report\n\n")
        mdf.write("## Overview\n")
        mdf.write(f"- **Total States / Union Territories Covered**: {len(files)}\n")
        mdf.write(f"- **Total Destination Records**: {total_records:,}\n")
        mdf.write(f"- **Total User Reviews Analyzed**: {int(total_reviews):,}\n")
        mdf.write(f"- **Common Schema Features**: 65 core fields (title, address, rating, price, category, website, location coordinates, operating hours, etc.)\n\n")

        mdf.write("## State-by-State Breakdown\n\n")
        mdf.write("| State / Union Territory | File | Total Places | Avg Rating | Total Reviews | Top Categories | Sample Places |\n")
        mdf.write("|---|---|---:|---:|---:|---|---|\n")
        
        for _, r in df_state.iterrows():
            mdf.write(f"| {r['state_ut']} | `{r['filename']}` | {r['total_destinations']} | {r['avg_rating']} | {r['total_reviews']:,} | {r['top_categories']} | {r['sample_places']} |\n")

        mdf.write("\n## Top Attraction Categories Across India\n\n")
        top_cats = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)[:15]
        for cat, cnt in top_cats:
            mdf.write(f"- **{cat}**: {cnt:,} locations\n")
            
        mdf.write("\n## Core Fields Available for Travel Recommendation Engine\n")
        mdf.write("1. **Destination Identification**: `title`, `subTitle`, `description`, `placeId`\n")
        mdf.write("2. **Geographic Coordinates**: `location/lat`, `location/lng`, `city`, `state`, `postalCode`\n")
        mdf.write("3. **Ratings & Crowd Insights**: `totalScore`, `reviewsCount`, `popularTimesHistogram`, `reviewsDistribution`\n")
        mdf.write("4. **Operational & Pricing Details**: `openingHours`, `price`, `website`, `phone`, `address`\n")
        mdf.write("5. **Categorization & Tags**: `categoryName`, `categories`, `placesTags`\n")
        
    print(f"✓ Saved state-wise MD report to: {md_out}")

if __name__ == "__main__":
    analyze_state_wise_data()
