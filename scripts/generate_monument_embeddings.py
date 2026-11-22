#!/usr/bin/env python3
"""
Phase 4B: ResNet-18 512-Dimensional Visual Embedding Extractor
Extracts L2-normalized 512-d feature vectors from the trained best ResNet-18 model checkpoint
and saves aligned embedding matrix & metadata table.
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.models as models

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import MonumentDataset, get_transforms, load_canonical_classes

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

def select_device():
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

class ResNet18FeatureExtractor(nn.Module):
    """
    ResNet-18 Backbone Feature Extractor (512-dim output layer)
    """
    def __init__(self, trained_model):
        super(ResNet18FeatureExtractor, self).__init__()
        # Remove fc layer to leave average pooling layer (512-dim)
        self.features = nn.Sequential(*list(trained_model.children())[:-1])

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        # L2 Normalization
        norm = torch.norm(x, p=2, dim=1, keepdim=True)
        norm = torch.where(norm == 0, torch.ones_like(norm), norm)
        x = x / norm
        return x

def generate_embeddings(limit=None):
    print("==========================================")
    print(" PHASE 4B: GENERATING VISUAL EMBEDDINGS   ")
    print("==========================================")

    best_model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    if not os.path.exists(best_model_path):
        print(f"❌ Error: Model checkpoint not found at {best_model_path}")
        sys.exit(1)

    device = select_device()
    print(f"✓ Selected Device for Feature Extraction: {device}")

    # Load trained model checkpoint
    checkpoint = torch.load(best_model_path, map_location=device, weights_only=False)
    num_classes = checkpoint.get("num_classes", 24)

    full_model = models.resnet18(weights=None)
    in_features = full_model.fc.in_features
    full_model.fc = nn.Linear(in_features, num_classes)
    full_model.load_state_dict(checkpoint['model_state_dict'])

    extractor = ResNet18FeatureExtractor(full_model).to(device)
    extractor.eval()

    # Load canonical images manifest
    df_classes, _, _, _ = load_canonical_classes()
    
    # Load all canonical images across train_v2, val_v2, test_v2 in deterministic order
    tr = pd.read_csv(os.path.join(PROCESSED_DIR, "train_v2.csv"))
    va = pd.read_csv(os.path.join(PROCESSED_DIR, "val_v2.csv"))
    te = pd.read_csv(os.path.join(PROCESSED_DIR, "test_v2.csv"))

    df_all = pd.concat([tr, va, te], ignore_index=True)

    if limit and limit > 0:
        print(f"⚠️  Sanity Check Mode: Limiting to first {limit} images...")
        df_all = df_all.iloc[:limit].copy()

    total_images = len(df_all)
    print(f"Extracting 512-d embeddings for {total_images:,} images...")

    dataset = MonumentDataset(df_all, root_dir=ROOT_DIR, transform=get_transforms('val'))
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=0)

    all_embeddings = []
    metadata_rows = []

    current_id = 0
    with torch.no_grad():
        for i, (images, labels) in enumerate(tqdm(dataloader, desc="Extracting Embeddings")):
            images = images.to(device)
            feats = extractor(images)
            all_embeddings.append(feats.cpu().numpy())

            batch_slice = df_all.iloc[current_id : current_id + images.size(0)]
            for _, row in batch_slice.iterrows():
                metadata_rows.append({
                    "embedding_id": current_id,
                    "image_path": row['image_path'],
                    "class_name": row['class_name'],
                    "class_id": row['class_id'],
                    "destination_id": row['destination_id'],
                    "original_class_name": row['original_class_name']
                })
                current_id += 1

    embedding_matrix = np.vstack(all_embeddings).astype(np.float32)
    df_metadata = pd.DataFrame(metadata_rows)

    print("\n------------------------------------------")
    print(f"✓ Embedding Matrix Shape: {embedding_matrix.shape}")
    print(f"✓ Metadata Rows: {len(df_metadata)}")

    # Verify L2 Norm is approximately 1.0
    norms = np.linalg.norm(embedding_matrix, axis=1)
    print(f"✓ L2 Norm Check: Min={norms.min():.4f}, Max={norms.max():.4f}, Mean={norms.mean():.4f}")
    print("------------------------------------------")

    if not limit:
        npy_path = os.path.join(EMBEDDINGS_DIR, "monument_embeddings.npy")
        csv_path = os.path.join(EMBEDDINGS_DIR, "monument_metadata.csv")

        np.save(npy_path, embedding_matrix)
        df_metadata.to_csv(csv_path, index=False)

        print(f"✓ Saved embeddings matrix to: {npy_path}")
        print(f"✓ Saved metadata table to: {csv_path}")

    return embedding_matrix, df_metadata

def main():
    parser = argparse.ArgumentParser(description="Generate 512-d Visual Embeddings")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of images for sanity check")
    args = parser.parse_args()

    generate_embeddings(limit=args.limit)

if __name__ == "__main__":
    main()
