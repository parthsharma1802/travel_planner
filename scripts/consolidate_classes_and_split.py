#!/usr/bin/env python3
"""
Phase 3.5: Semantic Class Consolidation & Group-Aware Resplit Script
1. Creates backup of Phase 3 CSVs under data/reports/phase3_backup/
2. Defines landmark_classes.csv (24 canonical classes) & class_consolidation_mapping.csv
3. Maps all 3,572 canonical images from 26 raw labels -> 24 canonical classes
4. Performs reproducible 70/15/15 group-aware split (seed 42) ensuring 0 leakage
5. Exports train_v2.csv, val_v2.csv, test_v2.csv, and phase3_5_class_distribution.csv
"""

import os
import shutil
import random
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")
BACKUP_DIR = os.path.join(REPORTS_DIR, "phase3_backup")

RANDOM_SEED = 42

def backup_phase3():
    print("==========================================")
    print(" 1. BACKING UP PHASE 3 CSV FILES          ")
    print("==========================================")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    for fname in ["train.csv", "val.csv", "test.csv"]:
        src = os.path.join(PROCESSED_DIR, fname)
        dst = os.path.join(BACKUP_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✓ Backed up {fname} -> {dst}")

def create_canonical_mappings():
    print("\n==========================================")
    print(" 2. CREATING CANONICAL CLASS MAPPINGS    ")
    print("==========================================")
    
    # 26 original classes -> 24 canonical classes
    consolidation_data = [
        ("Ajanta Caves", "Ajanta Caves", "IND_AJANTA_CAVES", "Original class preserved"),
        ("alai_darwaza", "Alai Darwaza", "IND_ALAI_DARWAZA", "Cleaned formatting"),
        ("alai_minar", "Alai Minar", "IND_ALAI_MINAR", "Cleaned formatting"),
        ("basilica_of_bom_jesus", "Basilica of Bom Jesus", "IND_BASILICA_OF_BOM_JESUS", "Cleaned formatting"),
        ("Charar-E- Sharif", "Charar-E-Sharif", "UNMAPPED_CHARAR-E-SHARIF", "Original class preserved"),
        ("charminar", "Charminar", "IND_CHARMINAR", "Cleaned formatting"),
        ("Chhota_Imambara", "Chhota Imambara", "IND_CHHOTA_IMAMBARA", "Cleaned formatting"),
        ("Ellora Caves", "Ellora Caves", "IND_ELLORA_CAVES", "Original class preserved"),
        ("Fatehpur Sikri", "Fatehpur Sikri", "IND_FATEHPUR_SIKRI", "Original class preserved"),
        ("Gateway of India", "Gateway of India", "IND_GATEWAY_OF_INDIA", "Original class preserved"),
        ("golden temple", "Golden Temple", "IND_GOLDEN_TEMPLE", "Cleaned formatting"),
        ("Hawa mahal", "Hawa Mahal", "IND_HAWA_MAHAL", "Merged into canonical Hawa Mahal"),
        ("hawa mahal pics", "Hawa Mahal", "IND_HAWA_MAHAL", "Merged into canonical Hawa Mahal"),
        ("Humayun_s Tomb", "Humayun's Tomb", "IND_HUMAYUN_S_TOMB", "Cleaned formatting"),
        ("India_gate", "India Gate", "IND_INDIA_GATE", "Merged into canonical India Gate"),
        ("India gate pics", "India Gate", "IND_INDIA_GATE", "Merged into canonical India Gate"),
        ("iron_pillar", "Iron Pillar", "UNMAPPED_IRON_PILLAR", "Cleaned formatting"),
        ("jamali_kamali_tomb", "Jamali Kamali Tomb", "IND_JAMALI_KAMALI_TOMB", "Cleaned formatting"),
        ("Khajuraho", "Khajuraho", "IND_KHAJURAHO", "Original class preserved"),
        ("lotus_temple", "Lotus Temple", "IND_LOTUS_TEMPLE", "Cleaned formatting"),
        ("mysore_palace", "Mysore Palace", "IND_MYSORE_PALACE", "Cleaned formatting"),
        ("qutub_minar", "Qutub Minar", "IND_QUTUB_MINAR", "Cleaned formatting"),
        ("Sun Temple Konark", "Sun Temple Konark", "IND_SUN_TEMPLE_KONARK", "Original class preserved"),
        ("tajmahal", "Taj Mahal", "IND_TAJMAHAL", "Cleaned formatting"),
        ("tanjavur temple", "Tanjavur Temple", "IND_TANJAVUR_TEMPLE", "Cleaned formatting"),
        ("victoria memorial", "Victoria Memorial", "IND_VICTORIA_MEMORIAL", "Cleaned formatting"),
    ]

    df_mapping = pd.DataFrame(consolidation_data, columns=[
        "original_class_name", "canonical_class_name", "destination_id", "reason"
    ])

    # Extract 24 unique canonical classes sorted alphabetically
    canonical_classes = sorted(df_mapping['canonical_class_name'].unique())
    canonical_class_df = pd.DataFrame([
        {
            "class_id": i,
            "class_name": cname,
            "destination_id": df_mapping[df_mapping['canonical_class_name'] == cname]['destination_id'].iloc[0]
        }
        for i, cname in enumerate(canonical_classes)
    ])

    # Map canonical_class_id back into df_mapping
    name_to_cid = dict(zip(canonical_class_df['class_name'], canonical_class_df['class_id']))
    df_mapping['canonical_class_id'] = df_mapping['canonical_class_name'].map(name_to_cid)

    # Save CSV files
    class_csv_path = os.path.join(PROCESSED_DIR, "landmark_classes.csv")
    map_csv_path = os.path.join(PROCESSED_DIR, "class_consolidation_mapping.csv")

    canonical_class_df[['class_id', 'class_name', 'destination_id']].to_csv(class_csv_path, index=False)
    df_mapping[['original_class_name', 'canonical_class_name', 'canonical_class_id', 'destination_id', 'reason']].to_csv(map_csv_path, index=False)

    print(f"✓ Saved landmark_classes.csv ({len(canonical_class_df)} classes) to: {class_csv_path}")
    print(f"✓ Saved class_consolidation_mapping.csv ({len(df_mapping)} mappings) to: {map_csv_path}")

    return df_mapping, canonical_class_df, name_to_cid

def consolidate_and_split(df_mapping, canonical_class_df, name_to_cid):
    print("\n==========================================")
    print(" 3. CONSOLIDATING LABELS & RESPLITTING   ")
    print("==========================================")
    
    # Load all Phase 3 canonical images across train, val, test CSVs
    tr = pd.read_csv(os.path.join(BACKUP_DIR, "train.csv"))
    va = pd.read_csv(os.path.join(BACKUP_DIR, "val.csv"))
    te = pd.read_csv(os.path.join(BACKUP_DIR, "test.csv"))

    df_all = pd.concat([tr, va, te], ignore_index=True)
    print(f"Combined total canonical images from Phase 3: {len(df_all)}")

    # Map original_class_name to new canonical info
    orig_to_canon = dict(zip(df_mapping['original_class_name'], df_mapping['canonical_class_name']))
    orig_to_dest = dict(zip(df_mapping['original_class_name'], df_mapping['destination_id']))

    df_all['original_class_name'] = df_all['class_name']
    df_all['class_name'] = df_all['original_class_name'].map(orig_to_canon)
    df_all['class_id'] = df_all['class_name'].map(name_to_cid)
    df_all['destination_id'] = df_all['original_class_name'].map(orig_to_dest)

    # Perform group-aware stratified 70/15/15 split (seed 42)
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    group_to_rows = defaultdict(list)
    for idx, row in df_all.iterrows():
        group_to_rows[row['near_duplicate_group_id']].append(row)

    groups = []
    for gid, rows in group_to_rows.items():
        c_counts = Counter([r['class_name'] for r in rows])
        dom_class = c_counts.most_common(1)[0][0]
        groups.append((gid, dom_class, rows))

    random.shuffle(groups)

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

    df_train_v2 = pd.DataFrame(train_rows).reset_index(drop=True)
    df_val_v2 = pd.DataFrame(val_rows).reset_index(drop=True)
    df_test_v2 = pd.DataFrame(test_rows).reset_index(drop=True)

    print(f"\nResplit Results across 24 Canonical Classes:")
    print(f" - Train_v2: {len(df_train_v2)} images ({len(df_train_v2)/len(df_all)*100:.1f}%)")
    print(f" - Val_v2:   {len(df_val_v2)} images ({len(df_val_v2)/len(df_all)*100:.1f}%)")
    print(f" - Test_v2:  {len(df_test_v2)} images ({len(df_test_v2)/len(df_all)*100:.1f}%)")

    export_cols = [
        'image_path', 'class_name', 'class_id', 'destination_id',
        'original_class_name', 'duplicate_group_id', 'near_duplicate_group_id'
    ]

    df_train_exp = df_train_v2[export_cols]
    df_val_exp = df_val_v2[export_cols]
    df_test_exp = df_test_v2[export_cols]

    tr_v2_path = os.path.join(PROCESSED_DIR, "train_v2.csv")
    va_v2_path = os.path.join(PROCESSED_DIR, "val_v2.csv")
    te_v2_path = os.path.join(PROCESSED_DIR, "test_v2.csv")

    df_train_exp.to_csv(tr_v2_path, index=False)
    df_val_exp.to_csv(va_v2_path, index=False)
    df_test_exp.to_csv(te_v2_path, index=False)

    # Overwrite train.csv, val.csv, test.csv for primary compatibility
    df_train_exp.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False)
    df_val_exp.to_csv(os.path.join(PROCESSED_DIR, "val.csv"), index=False)
    df_test_exp.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False)

    print(f"✓ Saved train_v2.csv & train.csv ({len(df_train_exp)} rows)")
    print(f"✓ Saved val_v2.csv & val.csv ({len(df_val_exp)} rows)")
    print(f"✓ Saved test_v2.csv & test.csv ({len(df_test_exp)} rows)")

    # 4. Generate phase3_5_class_distribution.csv
    dist_records = []
    for cname in canonical_class_df['class_name']:
        tr_cnt = len(df_train_exp[df_train_exp['class_name'] == cname])
        va_cnt = len(df_val_exp[df_val_exp['class_name'] == cname])
        te_cnt = len(df_test_exp[df_test_exp['class_name'] == cname])
        tot_cnt = tr_cnt + va_cnt + te_cnt
        dist_records.append({
            "canonical_class": cname,
            "total_images": tot_cnt,
            "train": tr_cnt,
            "val": va_cnt,
            "test": te_cnt
        })

    df_dist = pd.DataFrame(dist_records)
    dist_csv_path = os.path.join(REPORTS_DIR, "phase3_5_class_distribution.csv")
    df_dist.to_csv(dist_csv_path, index=False)
    print(f"✓ Saved phase3_5_class_distribution.csv to: {dist_csv_path}")

    return df_train_exp, df_val_exp, df_test_exp, df_dist

def main():
    backup_phase3()
    df_mapping, canonical_class_df, name_to_cid = create_canonical_mappings()
    consolidate_and_split(df_mapping, canonical_class_df, name_to_cid)

if __name__ == "__main__":
    main()
