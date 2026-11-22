#!/usr/bin/env python3
"""
Phase 3: Monument Dataset Cleaning, Group-Aware Stratified Splitting Script
Cleanly deduplicates raw monument images, handles near-duplicate grouping to prevent leakage,
executes a reproducible 70/15/15 train/val/test split, and outputs manifest CSVs.
"""

import os
import shutil
import random
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_EXTRACTED_DIR = os.path.join(ROOT_DIR, "data", "raw", "extracted", "indian_monuments")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
PROCESSED_MONUMENTS_DIR = os.path.join(PROCESSED_DIR, "monuments")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

RANDOM_SEED = 42

def load_audit_metadata():
    img_csv = os.path.join(REPORTS_DIR, "image_quality_report.csv")
    dup_csv = os.path.join(REPORTS_DIR, "duplicate_report.csv")
    map_csv = os.path.join(REPORTS_DIR, "destination_mapping.csv")
    
    df_img = pd.read_csv(img_csv)
    df_dup = pd.read_csv(dup_csv)
    df_map = pd.read_csv(map_csv) if os.path.exists(map_csv) else pd.DataFrame()
    
    df_merged = pd.merge(df_img, df_dup[['filepath', 'duplicate_status', 'sha256', 'phash']], on='filepath', suffixes=('', '_dup'))
    return df_merged, df_map

def clean_and_group(df_merged, df_map):
    print("==========================================")
    print(" 1. DEDUPLICATING & GROUPING IMAGES      ")
    print("==========================================")
    
    os.makedirs(PROCESSED_MONUMENTS_DIR, exist_ok=True)
    
    dest_id_map = {}
    mapped_count = 0
    unmapped_list = []
    
    if not df_map.empty:
        for _, row in df_map.iterrows():
            cv_class = row['original_cv_name']
            conf = row['confidence_pct']
            match = row['matched_tourism_destination']
            
            if conf >= 75.0 and match != 'N/A':
                clean_dest_id = "IND_" + cv_class.upper().replace(' ', '_').replace('-', '_').replace('PICS', '').strip('_')
                dest_id_map[cv_class] = clean_dest_id
                mapped_count += 1
            else:
                dest_id_map[cv_class] = f"UNMAPPED_{cv_class.upper()}"
                unmapped_list.append(cv_class)

    valid_df = df_merged[~df_merged['is_corrupt']].copy()
    print(f"Total valid raw images: {len(valid_df)}")
    
    # 1. Group by SHA-256 exact hash to pick 1 canonical image per exact hash
    canonical_records = []
    sha_groups = valid_df.groupby('sha256')
    
    exact_duplicates_removed = 0
    
    for sha, group in sha_groups:
        if sha == "N/A":
            for _, row in group.iterrows():
                canonical_records.append(row)
        else:
            canonical_records.append(group.iloc[0])
            exact_duplicates_removed += (len(group) - 1)
            
    df_canonical = pd.DataFrame(canonical_records).reset_index(drop=True)
    print(f"Exact duplicates removed: {exact_duplicates_removed}")
    print(f"Canonical unique image count: {len(df_canonical)}")
    
    # 2. Group globally by pHash for near duplicates
    phash_to_gid = {}
    gid_counter = 1
    
    # Count phash occurrences across canonical set
    phash_counts = Counter(df_canonical['phash'])
    for phash, count in phash_counts.items():
        if phash != "N/A" and count > 1:
            phash_to_gid[phash] = f"ND_GROUP_{gid_counter:04d}"
            gid_counter += 1

    near_dup_group_ids = []
    for idx, row in df_canonical.iterrows():
        ph = row['phash']
        if ph in phash_to_gid:
            near_dup_group_ids.append(phash_to_gid[ph])
        else:
            near_dup_group_ids.append(f"SINGLE_{idx:04d}")

    df_canonical['near_dup_group_id'] = near_dup_group_ids
    
    # 3. Copy canonical images
    print("\nCopying canonical images to data/processed/monuments/...")
    processed_paths = []
    
    classes = sorted(df_canonical['class_name'].unique())
    class_to_id = {c: i for i, c in enumerate(classes)}
    
    for idx, row in df_canonical.iterrows():
        orig_rel_path = row['filepath']
        orig_abs_path = os.path.join(ROOT_DIR, orig_rel_path)
        
        c_name = row['class_name']
        c_dir = os.path.join(PROCESSED_MONUMENTS_DIR, c_name)
        os.makedirs(c_dir, exist_ok=True)
        
        fname = os.path.basename(orig_rel_path)
        dest_filename = f"img_{idx:04d}_{fname}"
        dest_abs_path = os.path.join(c_dir, dest_filename)
        
        if not os.path.exists(dest_abs_path):
            shutil.copy2(orig_abs_path, dest_abs_path)
            
        proc_rel_path = os.path.relpath(dest_abs_path, ROOT_DIR)
        processed_paths.append(proc_rel_path)
        
    df_canonical['processed_image_path'] = processed_paths
    df_canonical['class_id'] = df_canonical['class_name'].map(class_to_id)
    df_canonical['destination_id'] = df_canonical['class_name'].map(lambda c: dest_id_map.get(c, f"UNMAPPED_{c.upper()}"))
    
    return df_canonical, classes, class_to_id, unmapped_list

def perform_stratified_group_split(df_canonical):
    print("\n==========================================")
    print(" 2. PERFORMING GROUP-AWARE 70/15/15 SPLIT")
    print("==========================================")
    
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    # Map each near_dup_group_id to all its rows
    group_to_rows = defaultdict(list)
    for idx, row in df_canonical.iterrows():
        group_to_rows[row['near_dup_group_id']].append(row)
        
    # Group metadata: (group_id, class_name, rows)
    groups = []
    for gid, rows in group_to_rows.items():
        # Determine dominant class for group
        c_counts = Counter([r['class_name'] for r in rows])
        dom_class = c_counts.most_common(1)[0][0]
        groups.append((gid, dom_class, rows))
        
    # Shuffle groups
    random.shuffle(groups)
    
    # Per class group splitting
    class_groups = defaultdict(list)
    for g in groups:
        class_groups[g[1]].append(g)
        
    train_rows, val_rows, test_rows = [], [], []
    
    for c_name, c_g_list in class_groups.items():
        n = len(c_g_list)
        n_tr = max(1, int(round(n * 0.70)))
        n_va = max(1, int(round(n * 0.15)))
        
        tr_g = c_g_list[:n_tr]
        va_g = c_g_list[n_tr:n_tr + n_va]
        te_g = c_g_list[n_tr + n_va:]
        
        if not te_g and len(tr_g) > 2:
            te_g = [tr_g.pop()]
            
        for g in tr_g:
            train_rows.extend(g[2])
        for g in va_g:
            val_rows.extend(g[2])
        for g in te_g:
            test_rows.extend(g[2])

    df_train = pd.DataFrame(train_rows).reset_index(drop=True)
    df_val = pd.DataFrame(val_rows).reset_index(drop=True)
    df_test = pd.DataFrame(test_rows).reset_index(drop=True)

    print(f"Train split: {len(df_train)} images ({len(df_train)/len(df_canonical)*100:.1f}%)")
    print(f"Val split:   {len(df_val)} images ({len(df_val)/len(df_canonical)*100:.1f}%)")
    print(f"Test split:  {len(df_test)} images ({len(df_test)/len(df_canonical)*100:.1f}%)")

    export_cols = [
        'processed_image_path', 'class_name', 'class_id', 'destination_id',
        'sha256', 'near_dup_group_id', 'filepath'
    ]
    rename_dict = {
        'processed_image_path': 'image_path',
        'sha256': 'duplicate_group_id',
        'near_dup_group_id': 'near_duplicate_group_id',
        'filepath': 'original_path'
    }

    df_train_exp = df_train[export_cols].rename(columns=rename_dict)
    df_val_exp = df_val[export_cols].rename(columns=rename_dict)
    df_test_exp = df_test[export_cols].rename(columns=rename_dict)

    df_train_exp.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False)
    df_val_exp.to_csv(os.path.join(PROCESSED_DIR, "val.csv"), index=False)
    df_test_exp.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False)

    print(f"✓ Exported train.csv ({len(df_train_exp)} rows)")
    print(f"✓ Exported val.csv ({len(df_val_exp)} rows)")
    print(f"✓ Exported test.csv ({len(df_test_exp)} rows)")

    return df_train_exp, df_val_exp, df_test_exp

def main():
    df_merged, df_map = load_audit_metadata()
    df_canonical, classes, class_to_id, unmapped_list = clean_and_group(df_merged, df_map)
    df_train, df_val, df_test = perform_stratified_group_split(df_canonical)
    
    if unmapped_list:
        unmapped_df = pd.DataFrame({"unmapped_class": unmapped_list, "action": "Requires manual review & tourism database entry"})
        unmapped_csv = os.path.join(REPORTS_DIR, "unmapped_classes.csv")
        unmapped_df.to_csv(unmapped_csv, index=False)
        print(f"✓ Saved unmapped classes ({len(unmapped_list)}) to: {unmapped_csv}")

if __name__ == "__main__":
    main()
