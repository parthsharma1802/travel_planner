#!/usr/bin/env python3
"""
Phase 4B: FAISS CPU Index Builder Script
Constructs an exact Inner Product / Cosine Similarity FAISS CPU Index
for 512-dimensional L2-normalized visual embeddings.
"""

import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import numpy as np
import faiss

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")

def build_index(sample_mode=False):
    print("==========================================")
    print(" PHASE 4B: BUILDING FAISS CPU INDEX      ")
    print("==========================================")

    npy_path = os.path.join(EMBEDDINGS_DIR, "monument_embeddings.npy")
    
    if sample_mode:
        print("⚠️  Sanity Check Mode: Generating 5 random L2-normalized sample vectors...")
        vecs = np.random.randn(5, 512).astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        embeddings = vecs / norms
    else:
        if not os.path.exists(npy_path):
            print(f"❌ Error: Embeddings file not found at {npy_path}")
            print("Please run embedding generation first: python scripts/generate_monument_embeddings.py")
            sys.exit(1)
            
        embeddings = np.load(npy_path).astype(np.float32)

    num_vectors, dim = embeddings.shape
    print(f"Loaded {num_vectors:,} vectors of dimension {dim}")

    # Build FAISS IndexFlatIP (Inner Product = Cosine Similarity for L2-normalized vectors)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print(f"✓ FAISS Index built with {index.ntotal} vectors.")

    if not sample_mode:
        index_path = os.path.join(EMBEDDINGS_DIR, "monuments.index")
        faiss.write_index(index, index_path)
        print(f"✓ Saved FAISS index to: {index_path}")

    return index

def main():
    parser = argparse.ArgumentParser(description="Build FAISS CPU Index for Monument Embeddings")
    parser.add_argument("--sample", action="store_true", help="Sample mode for quick sanity check")
    args = parser.parse_args()

    build_index(sample_mode=args.sample)

if __name__ == "__main__":
    main()
