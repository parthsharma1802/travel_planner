#!/usr/bin/env python3
"""
Phase 4B: Visual Retrieval Representative Examples Plotter
Generates 5 visual retrieval grid examples showing query image and Top-4 retrieved images
with similarity scores and destination names.
Saves PNG plots to data/reports/retrieval_examples/
"""

import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from scripts.search_similar_images import search_image

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")
OUTPUT_DIR = os.path.join(REPORTS_DIR, "retrieval_examples")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_visual_examples(num_examples=5):
    print("==========================================")
    print(" GENERATING VISUAL RETRIEVAL EXAMPLES     ")
    print("==========================================")

    test_csv = os.path.join(PROCESSED_DIR, "test_v2.csv")
    if not os.path.exists(test_csv):
        print(f"❌ Error: {test_csv} not found")
        sys.exit(1)

    df_test = pd.read_csv(test_csv)
    
    # Pick representative samples from different classes
    sample_rows = df_test.drop_duplicates(subset=['class_name']).head(num_examples)

    print(f"Generating {len(sample_rows)} visual example plots in {OUTPUT_DIR}...")

    for ex_idx, (_, row) in enumerate(sample_rows.iterrows(), 1):
        query_path = os.path.join(ROOT_DIR, row['image_path'])
        class_name = row['class_name']

        if not os.path.exists(query_path):
            continue

        results, _ = search_image(query_path, top_k=5, aggregate=False)

        # Plot 1 query image + 4 top retrieved matches (excluding exact self-match if present)
        fig, axes = plt.subplots(1, 5, figsize=(16, 4))
        
        # Query Image
        img_q = Image.open(query_path).convert('RGB')
        axes[0].imshow(img_q)
        axes[0].set_title(f"QUERY:\n{class_name}", fontsize=10, color='blue', fontweight='bold')
        axes[0].axis('off')

        # Top-4 Retrieved Matches
        retrieved = [r for r in results if r['image_path'] != row['image_path']][:4]
        
        for i, res in enumerate(retrieved, 1):
            match_img_path = os.path.join(ROOT_DIR, res['image_path'])
            if os.path.exists(match_img_path):
                img_m = Image.open(match_img_path).convert('RGB')
                axes[i].imshow(img_m)
            
            sim_score = res['similarity_score']
            dest_name = res['tourism_info']['destination_name']
            
            color = 'green' if res['class_name'] == class_name else 'red'
            axes[i].set_title(f"Match #{i} ({sim_score:.3f})\n{dest_name}", fontsize=9, color=color)
            axes[i].axis('off')

        plt.suptitle(f"Visual Retrieval Example #{ex_idx}: {class_name}", fontsize=12, fontweight='bold')
        plt.tight_layout()

        out_png = os.path.join(OUTPUT_DIR, f"example_{ex_idx:02d}_{class_name.lower().replace(' ', '_')}.png")
        plt.savefig(out_png, dpi=200)
        plt.close()
        print(f"✓ Saved visual example #{ex_idx} plot to: {out_png}")

    print(f"\n✓ Generated {num_examples} visual retrieval plots in: {OUTPUT_DIR}")

def main():
    generate_visual_examples(num_examples=5)

if __name__ == "__main__":
    main()
