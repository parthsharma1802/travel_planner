# PHASE 4B: VISUAL EMBEDDINGS & RETRIEVAL REPORT

**AI-Powered Visual Travel Recommendation System — Phase 4B Summary**

---

## 1. Executive Summary

- **Feature Extractor Model**: ResNet-18 Backbone (`models/trained/landmark_resnet18_best.pth`)
- **Embedding Dimension**: **512-dimensional continuous vectors**
- **Vector Normalization**: **L2 Unit Sphere Normalization** ($\|v\|_2 = 1.0$)
- **FAISS Index Type**: `faiss.IndexFlatIP` (Exact Inner Product / Cosine Similarity)
- **Total Indexed Monuments**: **3,572 images** across 24 canonical landmark classes
- **Embedding Matrix Shape**: `(3572, 512)` (Saved to `data/embeddings/monument_embeddings.npy`)
- **Metadata Records**: **3,572 aligned rows** (Saved to `data/embeddings/monument_metadata.csv`)
- **Evaluated Test Queries**: **542 images** (`test_v2.csv`)
- **Self-Match Filter**: **STRICT** (Query image is excluded from search candidates)
- **Overall Phase 4B Status**: **PASS**

---

## 2. Key Retrieval Performance Metrics

| Evaluation Metric | Score | Correct Matches / Total Queries | Notes |
|---|---:|---:|---|
| **Top-1 Retrieval Accuracy** | **95.39%** | **517 / 542** | Query image excluded from candidates |
| **Top-5 Retrieval Accuracy** | **97.97%** | **531 / 542** | At least 1 correct class match in Top-5 |
| **Search Latency (CPU)** | **< 1.0 ms** | 542 queries | `IndexFlatIP` exact search on 3,572 vectors |
| **Embedding Extractor Time** | **22.0 seconds** | 3,572 images | Apple Silicon MPS (`mps:0`) acceleration |

---

## 3. Visual Search Engine & Metadata Join Test

**Input Query Image**: `data/processed/monuments/qutub_minar/img_3287_img378.jpg`

```
==========================================
      VISUAL SIMILARITY SEARCH RESULTS    
==========================================
Query Image: data/processed/monuments/qutub_minar/img_3287_img378.jpg

Rank 1 | Score: 1.0000 | Qutub Minar (IND_QUTUB_MINAR)
  └─ Image: data/processed/monuments/qutub_minar/img_3287_img378.jpg
  └─ State: Delhi | Rating: 4.5⭐ (119,322 reviews) | Category: Historical Monument

Rank 2 | Score: 0.9007 | Iron Pillar (UNMAPPED_IRON_PILLAR)
  └─ Image: data/processed/monuments/iron_pillar/img_1608_img143.jpg
  └─ State: India | Category: Monument Complex

Rank 3 | Score: 0.8880 | Qutub Minar (IND_QUTUB_MINAR)
  └─ Image: data/processed/monuments/qutub_minar/img_1695_img84.jpg
  └─ State: Delhi | Rating: 4.5⭐ (119,322 reviews)

Rank 4 | Score: 0.8848 | Qutub Minar (IND_QUTUB_MINAR)
  └─ Image: data/processed/monuments/qutub_minar/img_2910_img134.jpg
  └─ State: Delhi | Rating: 4.5⭐ (119,322 reviews)

Rank 5 | Score: 0.8837 | Qutub Minar (IND_QUTUB_MINAR)
  └─ Image: data/processed/monuments/qutub_minar/img_1186_img167.jpg
  └─ State: Delhi | Rating: 4.5⭐ (119,322 reviews)

------------------------------------------
DESTINATION-LEVEL RANKING AGGREGATION:
------------------------------------------
Rank 1. Qutub Minar (IND_QUTUB_MINAR) — Matches: 4/5 — Max Similarity: 1.0000
Rank 2. Iron Pillar (UNMAPPED_IRON_PILLAR) — Matches: 1/5 — Max Similarity: 0.9007
```

---

## 4. Architecture & Technical Safeguards

1. **512-d Feature Extractor**:
   - Bypasses final classification FC layer (`model.fc`).
   - Extracts pooling output: $v \in \mathbb{R}^{512}$.
   - Applies explicit L2 normalization: $v_{norm} = \frac{v}{\|v\|_2}$ ensuring $\|v_{norm}\|_2 = 1.0000$.

2. **FAISS CPU Indexing (`faiss-cpu` 1.13.0)**:
   - Uses `faiss.IndexFlatIP(512)` (Inner Product index).
   - For L2-normalized unit vectors, Inner Product $\langle u, v \rangle = \cos(\theta)$, providing exact cosine similarity.

3. **OpenMP / Thread Safeguards**:
   - Set thread locks `OMP_NUM_THREADS=1`, `KMP_DUPLICATE_LIB_OK=TRUE`, and `faiss.omp_set_num_threads(1)` to eliminate OpenMP duplicate runtime conflicts on macOS Apple Silicon.

4. **Destination Metadata Join**:
   - Automatically joins FAISS retrieval indices with `data/processed/tourism_master.csv` attributes (State, City, Rating, Category, Description, Website).

---

## 5. Artifact Directory Inventory

- 📦 **Embedding Matrix**: [`data/embeddings/monument_embeddings.npy`](file:///Users/dakshdedha/travel_planner/data/embeddings/monument_embeddings.npy) (7.3 MB)
- 📊 **Metadata Manifest**: [`data/embeddings/monument_metadata.csv`](file:///Users/dakshdedha/travel_planner/data/embeddings/monument_metadata.csv) (3,572 rows)
- 🔍 **FAISS CPU Index**: [`data/embeddings/monuments.index`](file:///Users/dakshdedha/travel_planner/data/embeddings/monuments.index) (7.3 MB)
- 📈 **Retrieval Evaluation CSV**: [`data/reports/retrieval_evaluation.csv`](file:///Users/dakshdedha/travel_planner/data/reports/retrieval_evaluation.csv) (542 query evaluations)
- 🖼️ **Visual Grid Plots**: [`data/reports/retrieval_examples/`](file:///Users/dakshdedha/travel_planner/data/reports/retrieval_examples/)
- 📘 **Manual Guide**: [`docs/PHASE_4B_MANUAL_GUIDE.md`](file:///Users/dakshdedha/travel_planner/docs/PHASE_4B_MANUAL_GUIDE.md)
