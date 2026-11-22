#!/usr/bin/env python3
"""
Phase 4B: Retrieval Pipeline Evaluation Script
Evaluates visual similarity retrieval accuracy on test_v2.csv queries (542 images).
Strictly excludes query image self-matches from search results.
Computes Top-1 & Top-5 retrieval accuracy and exports evaluation reports.
"""

import os
import sys

# Prevent OpenMP thread lock crashes & duplicate libomp conflicts on macOS Apple Silicon
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import faiss

# Limit FAISS CPU threads to 1 to prevent OpenMP multi-threading crashes on macOS Apple Silicon
faiss.omp_set_num_threads(1)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.models as models

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import MonumentDataset, get_transforms

MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

class ResNet18FeatureExtractor(nn.Module):
    def __init__(self, trained_model):
        super(ResNet18FeatureExtractor, self).__init__()
        self.features = nn.Sequential(*list(trained_model.children())[:-1])

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        norm = torch.norm(x, p=2, dim=1, keepdim=True)
        norm = torch.where(norm == 0, torch.ones_like(norm), norm)
        return x / norm

def select_device():
    # Use CPU for evaluation feature extraction to ensure 100% stability and zero thread/MPS conflicts
    return torch.device("cpu")

def evaluate_retrieval(limit=None):
    print("==========================================")
    print(" EVALUATING VISUAL RETRIEVAL PERFORMANCE ")
    print("==========================================")

    model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    index_path = os.path.join(EMBEDDINGS_DIR, "monuments.index")
    meta_path = os.path.join(EMBEDDINGS_DIR, "monument_metadata.csv")
    test_csv = os.path.join(PROCESSED_DIR, "test_v2.csv")

    for p in [model_path, index_path, meta_path, test_csv]:
        if not os.path.exists(p):
            print(f"❌ Missing file for evaluation: {p}")
            sys.exit(1)

    device = select_device()
    print(f"✓ Selected Device for Query Feature Extraction: {device}")
    
    # Read FAISS index first
    index = faiss.read_index(index_path)
    df_meta = pd.read_csv(meta_path)
    df_test = pd.read_csv(test_csv)

    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    num_classes = checkpoint.get("num_classes", 24)

    full_model = models.resnet18(weights=None)
    full_model.fc = nn.Linear(full_model.fc.in_features, num_classes)
    full_model.load_state_dict(checkpoint['model_state_dict'])

    extractor = ResNet18FeatureExtractor(full_model).to(device)
    extractor.eval()

    if limit and limit > 0:
        print(f"⚠️  Sanity Check Mode: Evaluating on first {limit} test images...")
        df_test = df_test.iloc[:limit].copy()

    total_queries = len(df_test)
    print(f"Extracting query embeddings for {total_queries:,} test images...")

    test_ds = MonumentDataset(df_test, root_dir=ROOT_DIR, transform=get_transforms('val'))
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=0)

    # Step 1: Extract all query embeddings to NumPy array first (avoids OpenMP / MPS thread conflicts)
    query_embeddings_list = []
    with torch.no_grad():
        for images, _ in test_loader:
            images = images.to(device)
            feats = extractor(images)
            query_embeddings_list.append(feats.cpu().numpy())

    query_embeddings = np.vstack(query_embeddings_list).astype(np.float32)
    print(f"✓ Extracted query embedding matrix shape: {query_embeddings.shape}")

    # Step 2: Search FAISS Index on CPU in a single batch
    print(f"Searching FAISS index for {total_queries:,} queries...")
    scores, indices = index.search(query_embeddings, 10)

    top1_hits = 0
    top5_hits = 0
    eval_records = []

    for i in range(total_queries):
        query_row = df_test.iloc[i]
        query_img_path = query_row['image_path']
        query_class = query_row['class_name']
        query_dest_id = query_row['destination_id']

        q_scores = scores[i]
        q_indices = indices[i]

        # Filter out exact query image self-match
        filtered_results = []
        for sc, idx in zip(q_scores, q_indices):
            cand_meta = df_meta.iloc[idx]
            if cand_meta['image_path'] != query_img_path:
                filtered_results.append((sc, cand_meta))

        top1_match = filtered_results[0][1] if len(filtered_results) > 0 else None
        top5_matches = [r[1] for r in filtered_results[:5]]

        top1_hit = (top1_match['class_name'] == query_class) if top1_match is not None else False
        top5_hit = any(m['class_name'] == query_class for m in top5_matches)

        if top1_hit:
            top1_hits += 1
        if top5_hit:
            top5_hits += 1

        eval_records.append({
            "query_image_path": query_img_path,
            "query_class": query_class,
            "query_destination_id": query_dest_id,
            "top1_retrieved_class": top1_match['class_name'] if top1_match is not None else "N/A",
            "top1_retrieved_score": float(filtered_results[0][0]) if len(filtered_results) > 0 else 0.0,
            "top1_hit": top1_hit,
            "top5_hit": top5_hit
        })

    top1_acc = (top1_hits / total_queries) * 100
    top5_acc = (top5_hits / total_queries) * 100

    print("\n------------------------------------------")
    print(f"Top-1 Retrieval Accuracy: {top1_acc:.2f}% ({top1_hits}/{total_queries})")
    print(f"Top-5 Retrieval Accuracy: {top5_acc:.2f}% ({top5_hits}/{total_queries})")
    print("------------------------------------------")

    if not limit:
        df_eval = pd.DataFrame(eval_records)
        eval_csv_path = os.path.join(REPORTS_DIR, "retrieval_evaluation.csv")
        df_eval.to_csv(eval_csv_path, index=False)
        print(f"✓ Saved retrieval evaluation CSV to: {eval_csv_path}")

        # Save Markdown Report
        md_path = os.path.join(REPORTS_DIR, "PHASE_4B_RETRIEVAL_REPORT.md")
        with open(md_path, "w") as f:
            f.write("# PHASE 4B: VISUAL EMBEDDINGS & RETRIEVAL REPORT\n\n")
            f.write("## 1. Executive Summary\n")
            f.write(f"- **Embedding Model**: ResNet-18 Feature Extractor (512-dim output)\n")
            f.write(f"- **FAISS Index Type**: `IndexFlatIP` (Exact Inner Product / Cosine Similarity)\n")
            f.write(f"- **Total Indexed Vectors**: {len(df_meta):,}\n")
            f.write(f"- **Evaluated Test Queries**: {total_queries:,}\n\n")

            f.write("## 2. Key Retrieval Performance Metrics\n\n")
            f.write(f"- **Top-1 Retrieval Accuracy**: **{top1_acc:.2f}%** ({top1_hits}/{total_queries})\n")
            f.write(f"- **Top-5 Retrieval Accuracy**: **{top5_acc:.2f}%** ({top5_hits}/{total_queries})\n\n")

            f.write("## 3. Architecture & Index Configuration\n")
            f.write("- **Embedding Dimensionality**: 512 dimensions\n")
            f.write("- **Normalization**: L2 Unit Sphere Normalization ($\|v\|_2 = 1.0$)\n")
            f.write("- **Self-Match Prevention**: Strict query-image filtering during evaluation\n")
            f.write("- **Tourism Integration**: Automatic join with `tourism_master.csv` attributes\n")

        print(f"✓ Saved retrieval report MD to: {md_path}")

    return top1_acc, top5_acc

def main():
    parser = argparse.ArgumentParser(description="Evaluate FAISS Visual Retrieval Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit test queries for sanity check")
    args = parser.parse_args()

    try:
        evaluate_retrieval(limit=args.limit)
    except Exception as exc:
        import traceback
        print(f"❌ Error during evaluation: {exc}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
