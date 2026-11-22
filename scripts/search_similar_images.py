#!/usr/bin/env python3
"""
Phase 4B: Visual Similarity Search & Destination Information Lookup
Given an input image (or external image), extracts 512-d embedding, searches FAISS index,
retrieves Top-K visually similar destinations, and joins metadata from tourism_master.csv.
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
from PIL import Image
import faiss

import torch
import torch.nn as nn
import torchvision.models as models

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import get_transforms
from scripts.generate_monument_embeddings import ResNet18FeatureExtractor

MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

def select_device():
    return torch.device("cpu")

def load_resources():
    model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    index_path = os.path.join(EMBEDDINGS_DIR, "monuments.index")
    meta_path = os.path.join(EMBEDDINGS_DIR, "monument_metadata.csv")
    tourism_path = os.path.join(PROCESSED_DIR, "tourism_master.csv")

    for p, name in [(model_path, "Model Checkpoint"), (index_path, "FAISS Index"), (meta_path, "Embeddings Metadata"), (tourism_path, "Tourism Master CSV")]:
        if not os.path.exists(p):
            print(f"❌ Error: Required file missing ({name}): {p}")
            sys.exit(1)

    device = select_device()
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    num_classes = checkpoint.get("num_classes", 24)

    full_model = models.resnet18(weights=None)
    full_model.fc = nn.Linear(full_model.fc.in_features, num_classes)
    full_model.load_state_dict(checkpoint['model_state_dict'])

    extractor = ResNet18FeatureExtractor(full_model).to(device)
    extractor.eval()

    index = faiss.read_index(index_path)
    df_meta = pd.read_csv(meta_path)
    df_tourism = pd.read_csv(tourism_path)

    return extractor, index, df_meta, df_tourism, device

def search_image(image_path, top_k=5, aggregate=False):
    extractor, index, df_meta, df_tourism, device = load_resources()

    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        sys.exit(1)

    # 1. Preprocess & extract embedding
    transform = get_transforms('val')
    image = Image.open(image_path).convert('RGB')
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        query_emb = extractor(tensor).cpu().numpy().astype(np.float32)

    # 2. Search FAISS Index
    scores, indices = index.search(query_emb, top_k)
    scores = scores[0]
    indices = indices[0]

    results = []
    for rank, (score, idx) in enumerate(zip(scores, indices), 1):
        meta_row = df_meta.iloc[idx]
        dest_id = meta_row['destination_id']
        cname = meta_row['class_name']
        img_p = meta_row['image_path']

        # Join tourism metadata
        t_info = {}
        t_matches = df_tourism[df_tourism['destination_id'] == dest_id]
        if not t_matches.empty:
            t_row = t_matches.iloc[0]
            t_info = {
                "destination_name": t_row.get("destination_name", cname),
                "state": t_row.get("state", "N/A"),
                "city": t_row.get("city_district", "N/A"),
                "rating": t_row.get("rating", "N/A"),
                "reviews_count": t_row.get("reviews_count", "N/A"),
                "category": t_row.get("category", "N/A"),
                "description": t_row.get("description", "N/A"),
                "website": t_row.get("website_url", "N/A")
            }
        else:
            t_info = {
                "destination_name": cname,
                "state": "India",
                "city": "N/A",
                "rating": "N/A",
                "reviews_count": "N/A",
                "category": "Landmark",
                "description": "N/A",
                "website": "N/A"
            }

        results.append({
            "rank": rank,
            "similarity_score": float(score),
            "image_path": img_p,
            "class_name": cname,
            "destination_id": dest_id,
            "tourism_info": t_info
        })

    if aggregate:
        # Aggregate Top-K results by destination_id
        dest_counts = {}
        dest_max_score = {}
        dest_details = {}

        for r in results:
            did = r['destination_id']
            dest_counts[did] = dest_counts.get(did, 0) + 1
            dest_max_score[did] = max(dest_max_score.get(did, 0.0), r['similarity_score'])
            dest_details[did] = r['tourism_info']

        sorted_dests = sorted(dest_counts.keys(), key=lambda d: (dest_counts[d], dest_max_score[d]), reverse=True)
        agg_results = []
        for rank, did in enumerate(sorted_dests, 1):
            agg_results.append({
                "rank": rank,
                "destination_id": did,
                "count": dest_counts[did],
                "max_similarity": dest_max_score[did],
                "info": dest_details[did]
            })
        return results, agg_results

    return results, None

def main():
    parser = argparse.ArgumentParser(description="Search Visually Similar Travel Destinations")
    parser.add_argument("--image", type=str, required=True, help="Path to query image file")
    parser.add_argument("--top-k", type=int, default=5, help="Number of Top-K results")
    parser.add_argument("--aggregate", action="store_true", help="Enable destination-level ranking aggregation")

    args = parser.parse_args()

    results, agg_results = search_image(args.image, top_k=args.top_k, aggregate=args.aggregate)

    print("==========================================")
    print("      VISUAL SIMILARITY SEARCH RESULTS    ")
    print("==========================================")
    print(f"Query Image: {args.image}\n")

    for r in results:
        print(f"Rank {r['rank']} | Score: {r['similarity_score']:.4f} | {r['class_name']} ({r['destination_id']})")
        print(f"  └─ Image: {r['image_path']}")
        info = r['tourism_info']
        print(f"  └─ State: {info['state']} | Rating: {info['rating']}⭐ ({info['reviews_count']} reviews)")
        print()

    if agg_results:
        print("------------------------------------------")
        print("DESTINATION-LEVEL RANKING AGGREGATION:")
        print("------------------------------------------")
        for a in agg_results:
            info = a['info']
            print(f"Rank {a['rank']}. {info['destination_name']} ({a['destination_id']}) — Matches: {a['count']}/{args.top_k} — Max Similarity: {a['max_similarity']:.4f}")

if __name__ == "__main__":
    main()
