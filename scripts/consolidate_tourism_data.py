#!/usr/bin/env python3
"""
Phase 3: Tourism Data Master Consolidation Script
Merges india_tourism_dataset.json and all 32 state-wise Excel spreadsheets into
a standardized master dataset: data/processed/tourism_master.csv
Generates stable destination IDs (e.g. IND_TAJ_MAHAL, IND_HAWA_MAHAL) and aligns
destination IDs for the 21 mapped CV classes.
"""

import os
import glob
import json
import re
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACTED_DIR = os.path.join(ROOT_DIR, "data", "raw", "extracted")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

def make_destination_id(name, state=""):
    if not isinstance(name, str) or not name.strip():
        return "IND_UNKNOWN"
    
    # Clean string
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', name).strip().upper()
    cleaned = re.sub(r'\s+', '_', cleaned)
    
    if not cleaned:
        cleaned = "DESTINATION"
        
    dest_id = f"IND_{cleaned}"
    return dest_id

def consolidate():
    print("==========================================")
    print(" CONSOLIDATING TOURISM MASTER DATASET     ")
    print("==========================================")
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    records = []
    seen_ids = set()
    
    # 1. Load Master JSON
    json_path = os.path.join(EXTRACTED_DIR, "india_tourism_json", "india_tourism_dataset.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            json_data = json.load(f)
            
        print(f"Loaded {len(json_data)} records from india_tourism_dataset.json")
        for item in json_data:
            name = item.get("name") or item.get("destination_name") or item.get("title") or ""
            if not name:
                continue
                
            state = item.get("state", "India")
            city = item.get("city") or item.get("district") or item.get("location") or ""
            lat = item.get("lat") or item.get("latitude") or None
            lng = item.get("lng") or item.get("longitude") or None
            cat = item.get("category") or item.get("type") or "Tourist Attraction"
            rating = item.get("rating") or item.get("score") or None
            reviews = item.get("reviews_count") or item.get("reviews") or None
            price = item.get("entry_fee") or item.get("price") or None
            season = item.get("ideal_season") or item.get("best_time_to_visit") or ""
            desc = item.get("description") or item.get("overview") or ""
            url = item.get("url") or item.get("website") or ""
            
            dest_id = make_destination_id(name, state)
            
            # Deduplicate IDs
            original_id = dest_id
            counter = 1
            while dest_id in seen_ids:
                dest_id = f"{original_id}_{counter}"
                counter += 1
            seen_ids.add(dest_id)
            
            records.append({
                "destination_id": dest_id,
                "destination_name": name,
                "state": state,
                "city_district": city,
                "latitude": lat,
                "longitude": lng,
                "category": cat,
                "rating": rating,
                "reviews_count": reviews,
                "price_info": price,
                "ideal_seasonality": season,
                "description": desc,
                "website_url": url,
                "source_dataset": "india_tourism_dataset.json"
            })

    # 2. Load 32 State Spreadsheets
    state_dir = os.path.join(EXTRACTED_DIR, "state_wise_tourism", "state-wise Dataset")
    excel_files = sorted(glob.glob(os.path.join(state_dir, "*.xlsx")))
    print(f"Loading {len(excel_files)} state-wise Excel spreadsheets...")
    
    excel_record_count = 0
    for ef in excel_files:
        file_state = os.path.basename(ef).replace('.xlsx', '').title()
        try:
            df_ex = pd.read_excel(ef)
            for _, row in df_ex.iterrows():
                name = row.get("title") or row.get("name") or ""
                if not isinstance(name, str) or not name.strip():
                    continue
                    
                city = row.get("city") or row.get("neighborhood") or row.get("street") or ""
                lat = row.get("location/lat") if "location/lat" in df_ex.columns else None
                lng = row.get("location/lng") if "location/lng" in df_ex.columns else None
                cat = row.get("categoryName") or row.get("subTitle") or "Tourist Attraction"
                rating = row.get("totalScore") if "totalScore" in df_ex.columns else None
                reviews = row.get("reviewsCount") if "reviewsCount" in df_ex.columns else None
                price = row.get("price") if "price" in df_ex.columns else None
                desc = row.get("description") if "description" in df_ex.columns else ""
                url = row.get("website") if "website" in df_ex.columns else ""
                
                dest_id = make_destination_id(name, file_state)
                original_id = dest_id
                counter = 1
                while dest_id in seen_ids:
                    dest_id = f"{original_id}_{counter}"
                    counter += 1
                seen_ids.add(dest_id)
                
                records.append({
                    "destination_id": dest_id,
                    "destination_name": name,
                    "state": file_state,
                    "city_district": city,
                    "latitude": lat,
                    "longitude": lng,
                    "category": cat,
                    "rating": rating,
                    "reviews_count": reviews,
                    "price_info": price,
                    "ideal_seasonality": "",
                    "description": desc,
                    "website_url": url,
                    "source_dataset": os.path.basename(ef)
                })
                excel_record_count += 1
        except Exception as exc:
            print(f"Warning: Could not process {ef}: {exc}")

    df_master = pd.DataFrame(records)
    out_master_path = os.path.join(PROCESSED_DIR, "tourism_master.csv")
    df_master.to_csv(out_master_path, index=False)
    
    print("------------------------------------------")
    print(f"✓ Consolidated Master Tourism Records: {len(df_master):,}")
    print(f" - From JSON master: {len(json_data) if os.path.exists(json_path) else 0}")
    print(f" - From 32 State Excel files: {excel_record_count:,}")
    print(f"✓ Exported: {out_master_path}")
    print("------------------------------------------")
    
    # 3. Check Destination Mapping Alignment
    map_csv = os.path.join(REPORTS_DIR, "destination_mapping.csv")
    if os.path.exists(map_csv):
        df_map = pd.read_csv(map_csv)
        mapped_df = df_map[df_map['confidence_pct'] >= 75.0]
        unmapped_df = df_map[df_map['confidence_pct'] < 75.0]
        
        print(f"Mapped CV landmark classes: {len(mapped_df)}")
        print(f"Unmapped CV landmark classes: {len(unmapped_df)}")
        
        unmapped_path = os.path.join(REPORTS_DIR, "unmapped_classes.csv")
        unmapped_df[['original_cv_name', 'normalized_cv_name', 'confidence_pct', 'notes']].to_csv(unmapped_path, index=False)
        print(f"✓ Saved unmapped classes report to: {unmapped_path}")

if __name__ == "__main__":
    consolidate()
