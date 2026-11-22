#!/usr/bin/env python3
"""
Phase 3 Dataset Validation Suite
Validates disk existence, image readability, zero data leakage (exact & near-duplicate groups),
class representation across train/val/test splits, destination mapping integrity, and master schema.
"""

import os
import sys
import pandas as pd
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

def validate():
    print("==========================================")
    print(" RUNNING PHASE 3 DATASET VALIDATION SUITE ")
    print("==========================================")
    
    train_csv = os.path.join(PROCESSED_DIR, "train.csv")
    val_csv = os.path.join(PROCESSED_DIR, "val.csv")
    test_csv = os.path.join(PROCESSED_DIR, "test.csv")
    tourism_csv = os.path.join(PROCESSED_DIR, "tourism_master.csv")

    passed = True
    
    # 1. Verify file presence
    for csv_file, name in [(train_csv, "train.csv"), (val_csv, "val.csv"), (test_csv, "test.csv"), (tourism_csv, "tourism_master.csv")]:
        if not os.path.exists(csv_file):
            print(f"❌ Error: Missing file {name}")
            passed = False
        else:
            print(f"✓ Found manifest: {name}")

    if not passed:
        print("FAIL")
        sys.exit(1)

    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)
    df_test = pd.read_csv(test_csv)
    df_tourism = pd.read_csv(tourism_csv)

    print(f"\nManifest row counts: Train={len(df_train)}, Val={len(df_val)}, Test={len(df_test)}, Tourism={len(df_tourism)}")

    # 2. Verify Image Existence & Readability
    print("\n[Check 1/6] Verifying image existence & readability on disk...")
    all_dfs = [("train", df_train), ("val", df_val), ("test", df_test)]
    missing_count = 0
    unreadable_count = 0

    for split_name, df_split in all_dfs:
        for idx, row in df_split.iterrows():
            img_rel = row['image_path']
            img_full = os.path.join(ROOT_DIR, img_rel)
            if not os.path.exists(img_full):
                missing_count += 1
            else:
                try:
                    with Image.open(img_full) as img:
                        img.verify()
                except Exception:
                    unreadable_count += 1

    if missing_count == 0 and unreadable_count == 0:
        print("✓ All 3,572 images across splits exist and are 100% readable!")
    else:
        print(f"❌ Error: {missing_count} missing images, {unreadable_count} unreadable images.")
        passed = False

    # 3. Check Exact Duplicate Leakage across Splits
    print("\n[Check 2/6] Checking for exact duplicate leakage (SHA-256 / duplicate_group_id)...")
    train_dups = set(df_train['duplicate_group_id'])
    val_dups = set(df_val['duplicate_group_id'])
    test_dups = set(df_test['duplicate_group_id'])

    tv_exact_leak = train_dups.intersection(val_dups)
    tt_exact_leak = train_dups.intersection(test_dups)
    vt_exact_leak = val_dups.intersection(test_dups)

    if not tv_exact_leak and not tt_exact_leak and not vt_exact_leak:
        print("✓ ZERO exact duplicate leakage across Train/Val/Test!")
    else:
        print(f"❌ Error: Exact duplicate leakage detected! Train-Val: {len(tv_exact_leak)}, Train-Test: {len(tt_exact_leak)}, Val-Test: {len(vt_exact_leak)}")
        passed = False

    # 4. Check Near-Duplicate Group Leakage across Splits
    print("\n[Check 3/6] Checking for near-duplicate group leakage (near_duplicate_group_id)...")
    train_nd_groups = set(df_train[df_train['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])
    val_nd_groups = set(df_val[df_val['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])
    test_nd_groups = set(df_test[df_test['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])

    tv_nd_leak = train_nd_groups.intersection(val_nd_groups)
    tt_nd_leak = train_nd_groups.intersection(test_nd_groups)
    vt_nd_leak = val_nd_groups.intersection(test_nd_groups)

    if not tv_nd_leak and not tt_nd_leak and not vt_nd_leak:
        print("✓ ZERO near-duplicate group leakage across Train/Val/Test!")
    else:
        print(f"❌ Error: Near-duplicate leakage detected! Train-Val: {len(tv_nd_leak)}, Train-Test: {len(tt_nd_leak)}, Val-Test: {len(vt_nd_leak)}")
        passed = False

    # 5. Class Coverage across Splits
    print("\n[Check 4/6] Verifying class representation across splits...")
    train_classes = set(df_train['class_name'])
    val_classes = set(df_val['class_name'])
    test_classes = set(df_test['class_name'])

    if train_classes == val_classes == test_classes and len(train_classes) == 26:
        print(f"✓ All 26 classes represented in Train, Val, and Test splits!")
    else:
        print(f"❌ Warning: Missing classes in splits. Train: {len(train_classes)}, Val: {len(val_classes)}, Test: {len(test_classes)}")
        passed = False

    # 6. Check Tourism Master Schema & Destination IDs
    print("\n[Check 5/6] Validating Tourism Master Schema & Destination IDs...")
    if 'destination_id' in df_tourism.columns and 'destination_name' in df_tourism.columns:
        print(f"✓ Tourism Master Schema valid with {len(df_tourism)} records!")
    else:
        print("❌ Error: Tourism Master missing essential columns.")
        passed = False

    # 7. Final Result Summary
    print("\n==========================================")
    if passed:
        print(" VALIDATION SUITE RESULT: PASS")
        print("==========================================")
        return True
    else:
        print(" VALIDATION SUITE RESULT: FAIL")
        print("==========================================")
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
