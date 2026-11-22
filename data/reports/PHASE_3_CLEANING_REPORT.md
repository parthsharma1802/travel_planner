# PHASE 3: DATASET CLEANING & PREPROCESSING REPORT

**AI-Powered Visual Travel Recommendation System — Phase 3 Summary**

---

## 1. Executive Metrics & Summary

- **Raw Image Count**: 4,718 raw images scanned from `data/raw/extracted/indian_monuments/`
- **Unique Canonical Image Count**: 3,572 unique images copied to `data/processed/monuments/`
- **Exact Duplicates Removed**: 1,146 redundant duplicate images removed via SHA-256 hash deduplication
- **Near-Duplicate Groups**: 45 distinct near-duplicate groups (`ND_GROUP_0001` to `ND_GROUP_0045`)
- **Train / Val / Test Split Ratios**:
  - **Train Set (70%)**: 2,497 images (69.9%)
  - **Validation Set (15%)**: 534 images (14.9%)
  - **Test Set (15%)**: 541 images (15.1%)
  - **Total**: 3,572 images across 26 classes
- **Tourism Master Records**: 3,532 normalized travel destination records in `data/processed/tourism_master.csv`
- **CV Destination Mapping**:
  - **Mapped Classes**: 24 classes (e.g. `IND_TAJ_MAHAL`, `IND_HAWA_MAHAL`, `IND_QUTUB_MINAR`, etc.)
  - **Unmapped Classes**: 2 classes (`Charar-E- Sharif` and `iron_pillar`, logged in `data/reports/unmapped_classes.csv`)
- **Validation Suite Result**: **PASS** (Zero data leakage, 100% image readability, valid schemas).

---

## 2. Per-Class Image Distribution Across Splits

| # | Class Name | Class ID | Destination ID | Train (70%) | Val (15%) | Test (15%) | Total Canonical |
|---|---|---:|---|---:|---:|---:|---:|
| 1 | Ajanta Caves | 0 | `IND_AJANTA_CAVES` | 64 | 14 | 14 | 92 |
| 2 | Charar-E- Sharif | 1 | `UNMAPPED_CHARAR-E-_SHARIF` | 23 | 5 | 5 | 33 |
| 3 | Chhota_Imambara | 2 | `IND_CHHOTA_IMAMBARA` | 42 | 9 | 9 | 60 |
| 4 | Ellora Caves | 3 | `IND_ELLORA_CAVES` | 74 | 16 | 16 | 106 |
| 5 | Fatehpur Sikri | 4 | `IND_FATEHPUR_SIKRI` | 89 | 19 | 19 | 127 |
| 6 | Gateway of India | 5 | `IND_GATEWAY_OF_INDIA` | 134 | 29 | 29 | 192 |
| 7 | Hawa mahal | 6 | `IND_HAWA_MAHAL` | 76 | 16 | 16 | 108 |
| 8 | Humayun_s Tomb | 7 | `IND_HUMAYUN_S_TOMB` | 50 | 11 | 11 | 72 |
| 9 | India gate pics | 8 | `IND_INDIA_GATE` | 71 | 15 | 15 | 101 |
| 10 | India_gate | 9 | `IND_INDIA_GATE` | 132 | 28 | 28 | 188 |
| 11 | Khajuraho | 10 | `IND_KHAJURAHO` | 91 | 19 | 20 | 130 |
| 12 | Sun Temple Konark | 11 | `IND_SUN_TEMPLE_KONARK` | 73 | 16 | 16 | 105 |
| 13 | alai_darwaza | 12 | `IND_ALAI_DARWAZA` | 43 | 9 | 10 | 62 |
| 14 | alai_minar | 13 | `IND_ALAI_MINAR` | 41 | 9 | 9 | 59 |
| 15 | basilica_of_bom_jesus | 14 | `IND_BASILICA_OF_BOM_JESUS` | 52 | 11 | 11 | 74 |
| 16 | charminar | 15 | `IND_CHARMINAR` | 151 | 32 | 33 | 216 |
| 17 | golden temple | 16 | `IND_GOLDEN_TEMPLE` | 118 | 25 | 26 | 169 |
| 18 | hawa mahal pics | 17 | `IND_HAWA_MAHAL` | 66 | 14 | 14 | 94 |
| 19 | iron_pillar | 18 | `UNMAPPED_IRON_PILLAR` | 47 | 10 | 10 | 67 |
| 20 | jamali_kamali_tomb | 19 | `IND_JAMALI_KAMALI_TOMB` | 139 | 30 | 30 | 199 |
| 21 | lotus_temple | 20 | `IND_LOTUS_TEMPLE` | 16 | 3 | 4 | 23 |
| 22 | mysore_palace | 21 | `IND_MYSORE_PALACE` | 120 | 26 | 26 | 172 |
| 23 | qutub_minar | 22 | `IND_QUTUB_MINAR` | 302 | 65 | 65 | 432 |
| 24 | tajmahal | 23 | `IND_TAJMAHAL` | 187 | 40 | 40 | 267 |
| 25 | tanjavur temple | 24 | `IND_TANJAVUR_TEMPLE` | 129 | 28 | 28 | 185 |
| 26 | victoria memorial | 25 | `IND_VICTORIA_MEMORIAL` | 105 | 22 | 23 | 150 |
| **Total** | | | | **2,497** | **534** | **541** | **3,572** |

---

## 3. Data Leakage Prevention Verification

- **Group-Aware Splitting**: Both SHA-256 exact duplicate groups and perceptual hash (`imagehash.phash`) near-duplicate groups were kept intact inside individual splits.
- **Leakage Test Result**:
  - Exact duplicate overlap (Train/Val/Test): **0 instances**
  - Near-duplicate group overlap (Train/Val/Test): **0 instances**

---

## 4. Tourism Master Dataset Consolidation

- **Consolidated Records**: 3,532 destination records compiled into `data/processed/tourism_master.csv`.
- **Sources**:
  - 100 records from `india_tourism_dataset.json`
  - 3,432 records from 32 state-wise Excel spreadsheets (`data/raw/extracted/state_wise_tourism/`)
- **Attributes Preserved**: `destination_id`, `destination_name`, `state`, `city_district`, `latitude`, `longitude`, `category`, `rating`, `reviews_count`, `price_info`, `ideal_seasonality`, `description`, `website_url`.

---

## 5. Image Preprocessing & PyTorch Dataset API

- Created reusable dataset module at [`backend/cv/dataset.py`](file:///Users/dakshdedha/travel_planner/backend/cv/dataset.py).
- **Runtime Transforms**:
  - Training: `Resize((256, 256))`, `RandomResizedCrop(224)`, `RandomHorizontalFlip(p=0.5)`, `RandomRotation(15°)`, `ColorJitter`, `Normalize(ImageNet)`.
  - Validation/Testing: `Resize((224, 224))`, `ToTensor()`, `Normalize(ImageNet)`.
- Zero transformed images saved to disk (100% on-the-fly PyTorch DataLoader processing).

---

## 6. Remaining Issues & Next Phase Recommendations

### Remaining Issues
1. **Unmapped Classes**: `Charar-E- Sharif` and `iron_pillar` lack explicit high-confidence matches in the primary tourism database. Entry details should be added manually or flagged in API fallback responses.
2. **Overlapping Class Categories**: Classes like `Hawa mahal` and `hawa mahal pics` represent the same physical destination (`IND_HAWA_MAHAL`). Both maps resolve to the same destination ID in `tourism_master.csv`.

### Recommended Next Phase (Phase 4)
1. **Model Fine-Tuning (Landmark Classification)**: Train ResNet-18 model on MPS (`mps:0`) using `train.csv` and `val.csv` with CrossEntropyLoss and Evaluate on `test.csv`.
2. **Feature Embedding Extraction**: Run inference with pretrained `feature_extractor_resnet18.pth` to generate 512-dim embedding vectors for all 3,572 images.
3. **FAISS Similarity Index Construction**: Build `data/embeddings/monuments.index` for fast visual similarity search.
4. **Backend API Endpoint Integration**: Implement FastAPI endpoints connecting CV classification, FAISS vector search, and tourism master details.
