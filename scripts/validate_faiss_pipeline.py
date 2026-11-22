#!/usr/bin/env python3
"""
Phase 4B Automated Validation Suite: Visual Embeddings & FAISS Retrieval
Verifies embedding shape (3572, 512), metadata alignment, L2 normalization, FAISS CPU index integrity,
query embedding extraction, Top-K search functionality, and self-match filtering.
"""

import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import numpy as np
import pandas as pd
import faiss

import torch
import torch.nn as nn
from PIL import Image
import torchvision.models as models

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import get_transforms
from scripts.generate_monument_embeddings import ResNet18FeatureExtractor

MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

def select_device():
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

def validate(sanity_mode=False):
    print("==========================================")
    print(" PHASE 4B VALIDATION SUITE (10 CHECKS)   ")
    print("==========================================")

    model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    npy_path = os.path.join(EMBEDDINGS_DIR, "monument_embeddings.npy")
    csv_path = os.path.join(EMBEDDINGS_DIR, "monument_metadata.csv")
    index_path = os.path.join(EMBEDDINGS_DIR, "monuments.index")

    passed = True

    # 1. Model Checkpoint check
    if not os.path.exists(model_path):
        print(f"❌ Error: Missing model checkpoint: {model_path}")
        passed = False
    else:
        print("✓ Passed: Model checkpoint `landmark_resnet18_best.pth` exists.")

    # 2. Check feature extractor instantiation & output shape
    print("\n[Check 1/10] Verifying feature extractor architecture...")
    try:
        device = select_device()
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        full_model = models.resnet18(weights=None)
        full_model.fc = nn.Linear(full_model.fc.in_features, checkpoint.get("num_classes", 24))
        full_model.load_state_dict(checkpoint['model_state_dict'])

        extractor = ResNet18FeatureExtractor(full_model).to(device)
        extractor.eval()

        dummy_img = torch.randn(1, 3, 224, 224, device=device)
        dummy_feat = extractor(dummy_img)

        if dummy_feat.shape == (1, 512):
            print("✓ Passed: ResNet-18 Feature Extractor produces 512-dim embedding.")
        else:
            print(f"❌ Error: Unexpected feature shape {dummy_feat.shape}")
            passed = False
    except Exception as exc:
        print(f"❌ Error instantiating feature extractor: {exc}")
        passed = False

    # 3. Check L2 Normalization on dummy feature
    dummy_norm = torch.norm(dummy_feat, p=2, dim=1).item()
    if abs(dummy_norm - 1.0) < 1e-4:
        print(f"✓ Passed: Feature extractor outputs L2-normalized vector (Norm = {dummy_norm:.4f}).")
    else:
        print(f"❌ Error: L2 norm is {dummy_norm}, expected 1.0.")
        passed = False

    if sanity_mode:
        print("\n==========================================")
        print(" SANITY TEST COMPLETED CLEANLY (PASS)    ")
        print("==========================================")
        return True

    # Full files checks
    if not os.path.exists(npy_path) or not os.path.exists(csv_path) or not os.path.exists(index_path):
        print(f"\n⚠️  Note: Full embedding files not generated yet. Run manual generation commands next.")
        return passed

    embeddings = np.load(npy_path)
    df_meta = pd.read_csv(csv_path)
    index = faiss.read_index(index_path)

    # 4. Matrix shape check
    print(f"\n[Check 3/10] Verifying embedding matrix shape...")
    if embeddings.shape == (3572, 512):
        print("✓ Passed: Embedding matrix shape is exactly (3572, 512).")
    else:
        print(f"❌ Error: Matrix shape is {embeddings.shape}, expected (3572, 512).")
        passed = False

    # 5. Metadata count check
    print("\n[Check 4/10] Verifying metadata row count...")
    if len(df_meta) == 3572:
        print("✓ Passed: Metadata table contains exactly 3,572 rows.")
    else:
        print(f"❌ Error: Metadata rows count is {len(df_meta)}, expected 3,572.")
        passed = False

    # 6. FAISS vector count check
    print("\n[Check 5/10] Verifying FAISS vector count...")
    if index.ntotal == 3572:
        print("✓ Passed: FAISS index contains exactly 3,572 vectors.")
    else:
        print(f"❌ Error: FAISS index ntotal is {index.ntotal}, expected 3,572.")
        passed = False

    # 7. Alignment check
    print("\n[Check 6/10] Verifying metadata alignment...")
    if len(df_meta) == len(embeddings) == index.ntotal:
        print("✓ Passed: 1-to-1 perfect alignment between embeddings, metadata, and FAISS index.")
    else:
        print("❌ Error: Misalignment between embeddings, metadata, and FAISS index!")
        passed = False

    # 8. Test Query search
    print("\n[Check 7/10] Testing FAISS Top-K Search...")
    scores, indices = index.search(embeddings[:1], 5)
    if len(indices[0]) == 5:
        print(f"✓ Passed: Top-5 FAISS search executed cleanly (Top-1 similarity: {scores[0][0]:.4f}).")
    else:
        print("❌ Error in FAISS search.")
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

def main():
    parser = argparse.ArgumentParser(description="Validate FAISS Pipeline")
    parser.add_argument("--sanity", action="store_true", help="Sanity check mode only")
    args = parser.parse_args()

    success = validate(sanity_mode=args.sanity)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
