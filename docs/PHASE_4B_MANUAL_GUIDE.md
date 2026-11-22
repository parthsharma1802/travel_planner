# Phase 4B: Visual Embeddings & FAISS Retrieval — Manual Execution Guide

This guide provides step-by-step instructions to manually generate **512-dimensional visual embeddings**, build the **FAISS CPU index**, evaluate retrieval performance, and query visually similar destinations on your **Apple Silicon M4 Mac (16 GB RAM)**.

---

## A. What Antigravity Created & Verified

All code modules have been written and verified with lightweight sanity tests:
- 🐍 [`scripts/generate_monument_embeddings.py`](file:///Users/dakshdedha/travel_planner/scripts/generate_monument_embeddings.py): ResNet-18 512-d L2-normalized embedding generator with `tqdm` progress bar.
- 🐍 [`scripts/build_faiss_index.py`](file:///Users/dakshdedha/travel_planner/scripts/build_faiss_index.py): Exact Inner Product FAISS CPU Index builder (`IndexFlatIP`).
- 🐍 [`scripts/search_similar_images.py`](file:///Users/dakshdedha/travel_planner/scripts/search_similar_images.py): Visual similarity search & tourism metadata joiner (`tourism_master.csv`).
- 🐍 [`scripts/evaluate_retrieval.py`](file:///Users/dakshdedha/travel_planner/scripts/evaluate_retrieval.py): Offline Top-1/Top-5 retrieval evaluator on `test_v2.csv` (query self-match excluded).
- 🐍 [`scripts/visualize_retrieval_examples.py`](file:///Users/dakshdedha/travel_planner/scripts/visualize_retrieval_examples.py): Generates 5 visual retrieval plot grids.
- 🐍 [`scripts/validate_faiss_pipeline.py`](file:///Users/dakshdedha/travel_planner/scripts/validate_faiss_pipeline.py): Pipeline validator.

---

## B. Step-by-Step Manual Terminal Execution

### Step 1: Activate Virtual Environment

Open terminal and run:

```bash
cd /Users/dakshdedha/travel_planner
source venv/bin/activate
```

---

### Step 2: Run Lightweight Code Sanity Test

```bash
python scripts/validate_faiss_pipeline.py --sanity
```
*Expected Output:* `SANITY TEST COMPLETED CLEANLY (PASS)`

---

### Step 3: Manually Generate Visual Embeddings (3,572 Canonical Images)

Extract 512-dimensional L2-normalized feature vectors using Apple Silicon MPS acceleration:

```bash
python scripts/generate_monument_embeddings.py
```

*What to expect:*
- Uses Apple Silicon MPS GPU acceleration for fast feature extraction.
- Displays `tqdm` progress bar (`100%|██████████| 112/112 [00:45<00:00]`).
- Time required: ~45–60 seconds.
- Output files:
  - `data/embeddings/monument_embeddings.npy` (matrix shape: `3572, 512`, size ~7.3 MB)
  - `data/embeddings/monument_metadata.csv` (3,572 rows)

---

### Step 4: Manually Build the FAISS CPU Index

Construct the exact cosine similarity FAISS CPU index:

```bash
python scripts/build_faiss_index.py
```

*What to expect:*
- Loads 3,572 vectors of dimension 512.
- Builds `faiss.IndexFlatIP(512)` on CPU in < 1 second.
- Output file: `data/embeddings/monuments.index` (~7.3 MB).

---

### Step 5: Manually Run Visual Retrieval Evaluation

Evaluate Top-1 and Top-5 retrieval accuracy on 542 test query images (query self-match filtered out):

```bash
python scripts/evaluate_retrieval.py
```

*What to expect:*
- Computes query embeddings and searches FAISS index.
- Output files:
  - `data/reports/retrieval_evaluation.csv`
  - `data/reports/PHASE_4B_RETRIEVAL_REPORT.md`

---

### Step 6: Generate Visual Example Plots

Generate 5 visual grid example plots:

```bash
python scripts/visualize_retrieval_examples.py
```

*Output files:* `data/reports/retrieval_examples/example_01_*.png`

---

### Step 7: Test Visual Search on Any Image

Test similarity search on an example image:

```bash
python scripts/search_similar_images.py --image data/processed/monuments/qutub_minar/img_3287_img378.jpg --top-k 5 --aggregate
```

---

## C. Hardware & Workload Information

- **Embedding Extraction**: Runs on **Apple Silicon MPS** (`mps:0`). GPU tensor processing makes extraction extremely fast (~45s for 3,572 images).
- **FAISS Similarity Search**: Runs on **CPU** using `faiss-cpu`. For 3,572 vectors, CPU exact search takes < 1 millisecond per query.
- **Error Recovery**: If interrupted, simply re-run `python scripts/generate_monument_embeddings.py`. Existing valid model weights are never modified.
