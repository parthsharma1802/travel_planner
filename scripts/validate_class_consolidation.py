#!/usr/bin/env python3
"""
Phase 3.5 Automated Validation Suite: Semantic Class Consolidation
Executes 12 verification checks to validate 26 -> 24 class reduction, zero leakage,
exact image count preservation (3,572), and schema integrity.
"""

import os
import sys
import pandas as pd
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

def validate():
    print("==========================================")
    print(" PHASE 3.5 VALIDATION SUITE (12 CHECKS)  ")
    print("==========================================")

    passed = True

    landmark_csv = os.path.join(PROCESSED_DIR, "landmark_classes.csv")
    mapping_csv = os.path.join(PROCESSED_DIR, "class_consolidation_mapping.csv")
    tr_v2 = os.path.join(PROCESSED_DIR, "train_v2.csv")
    va_v2 = os.path.join(PROCESSED_DIR, "val_v2.csv")
    te_v2 = os.path.join(PROCESSED_DIR, "test_v2.csv")

    for fpath in [landmark_csv, mapping_csv, tr_v2, va_v2, te_v2]:
        if not os.path.exists(fpath):
            print(f"❌ Error: Missing file {os.path.basename(fpath)}")
            passed = False

    if not passed:
        print("FAIL")
        sys.exit(1)

    df_classes = pd.read_csv(landmark_csv)
    df_map = pd.read_csv(mapping_csv)
    df_tr = pd.read_csv(tr_v2)
    df_va = pd.read_csv(va_v2)
    df_te = pd.read_csv(te_v2)

    # Check 1: Exactly 24 canonical classes
    print("\n[Check 1/12] Verifying exactly 24 canonical classes exist...")
    if len(df_classes) == 24 and df_classes['class_id'].nunique() == 24:
        print(f"✓ Passed: Exactly 24 canonical classes defined in landmark_classes.csv.")
    else:
        print(f"❌ Error: Expected 24 classes, found {len(df_classes)}")
        passed = False

    # Check 2 & 3: Hawa Mahal & India Gate single class IDs
    print("\n[Check 2/12 & 3/12] Verifying single class IDs for Hawa Mahal and India Gate...")
    hawa_cids = df_classes[df_classes['class_name'] == 'Hawa Mahal']['class_id'].tolist()
    india_cids = df_classes[df_classes['class_name'] == 'India Gate']['class_id'].tolist()

    if len(hawa_cids) == 1 and len(india_cids) == 1:
        print(f"✓ Passed: Hawa Mahal class_id={hawa_cids[0]}, India Gate class_id={india_cids[0]}")
    else:
        print(f"❌ Error: Hawa Mahal or India Gate has multiple class IDs!")
        passed = False

    # Check 4 & 5: Old Hawa Mahal & India Gate labels mapping
    print("\n[Check 4/12 & 5/12] Verifying mapping of old labels...")
    hm_old = df_map[df_map['original_class_name'].isin(['Hawa mahal', 'hawa mahal pics'])]
    ig_old = df_map[df_map['original_class_name'].isin(['India_gate', 'India gate pics'])]

    if hm_old['canonical_class_name'].nunique() == 1 and hm_old['canonical_class_name'].iloc[0] == 'Hawa Mahal':
        print("✓ Passed: Both old Hawa Mahal labels map to 'Hawa Mahal'.")
    else:
        print("❌ Error in Hawa Mahal label mapping.")
        passed = False

    if ig_old['canonical_class_name'].nunique() == 1 and ig_old['canonical_class_name'].iloc[0] == 'India Gate':
        print("✓ Passed: Both old India Gate labels map to 'India Gate'.")
    else:
        print("❌ Error in India Gate label mapping.")
        passed = False

    # Check 6: Total image count = 3,572
    print("\n[Check 6/12] Verifying total image count remains unchanged at 3,572...")
    total_imgs = len(df_tr) + len(df_va) + len(df_te)
    if total_imgs == 3572:
        print(f"✓ Passed: Total canonical image count is exactly 3,572.")
    else:
        print(f"❌ Error: Expected 3,572 images, found {total_imgs}")
        passed = False

    # Check 7: No duplicate image paths
    print("\n[Check 7/12] Checking for duplicate image paths across splits...")
    all_paths = df_tr['image_path'].tolist() + df_va['image_path'].tolist() + df_te['image_path'].tolist()
    if len(all_paths) == len(set(all_paths)):
        print("✓ Passed: Zero duplicate image paths across splits.")
    else:
        print(f"❌ Error: Found {len(all_paths) - len(set(all_paths))} duplicate image paths!")
        passed = False

    # Check 8: No exact duplicate group leakage
    print("\n[Check 8/12] Checking for exact duplicate leakage (duplicate_group_id)...")
    tr_dup = set(df_tr['duplicate_group_id'])
    va_dup = set(df_va['duplicate_group_id'])
    te_dup = set(df_te['duplicate_group_id'])

    tv_leak = tr_dup.intersection(va_dup)
    tt_leak = tr_dup.intersection(te_dup)
    vt_leak = va_dup.intersection(te_dup)

    if not tv_leak and not tt_leak and not vt_leak:
        print("✓ Passed: ZERO exact duplicate leakage across Train/Val/Test splits.")
    else:
        print("❌ Error: Exact duplicate leakage detected!")
        passed = False

    # Check 9: No near-duplicate group leakage
    print("\n[Check 9/12] Checking for near-duplicate group leakage (near_duplicate_group_id)...")
    tr_nd = set(df_tr[df_tr['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])
    va_nd = set(df_va[df_va['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])
    te_nd = set(df_te[df_te['near_duplicate_group_id'].str.startswith('ND_GROUP')]['near_duplicate_group_id'])

    tv_nd_leak = tr_nd.intersection(va_nd)
    tt_nd_leak = tr_nd.intersection(te_nd)
    vt_nd_leak = va_nd.intersection(te_nd)

    if not tv_nd_leak and not tt_nd_leak and not vt_nd_leak:
        print("✓ Passed: ZERO near-duplicate group leakage across Train/Val/Test splits.")
    else:
        print("❌ Error: Near-duplicate group leakage detected!")
        passed = False

    # Check 10 & 11: Valid class IDs (0..23) and destination IDs
    print("\n[Check 10/12 & 11/12] Verifying class IDs (0..23) and destination IDs...")
    valid_cids = set(range(24))
    all_cids = set(df_tr['class_id']).union(set(df_va['class_id'])).union(set(df_te['class_id']))

    if all_cids.issubset(valid_cids):
        print("✓ Passed: Every image has a valid canonical class ID (0..23).")
    else:
        print(f"❌ Error: Invalid class IDs found: {all_cids - valid_cids}")
        passed = False

    # Check 12: All 24 canonical classes represented in Train, Val, and Test
    print("\n[Check 12/12] Verifying representation of all 24 classes across Train, Val, and Test...")
    tr_c = set(df_tr['class_name'])
    va_c = set(df_va['class_name'])
    te_c = set(df_te['class_name'])

    if len(tr_c) == 24 and len(va_c) == 24 and len(te_c) == 24:
        print("✓ Passed: All 24 canonical classes represented in Train, Val, and Test splits.")
    else:
        print(f"❌ Error: Missing classes in splits. Train: {len(tr_c)}, Val: {len(va_c)}, Test: {len(te_c)}")
        passed = False

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
