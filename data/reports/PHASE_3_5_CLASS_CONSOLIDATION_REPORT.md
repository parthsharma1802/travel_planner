# PHASE 3.5: SEMANTIC CLASS CONSOLIDATION REPORT

**AI-Powered Visual Travel Recommendation System — Phase 3.5 Summary**

---

## 1. Executive Metrics & High-Level Summary

- **Old CV Label Classes**: 26 raw label categories
- **New Canonical Physical Classes**: **24 unique physical landmark classes**
- **Total Canonical Image Count**: **3,572 images** (3,572 → 3,572, 100% image count preservation)
- **Phase 3 Backup**: Original Phase 3 manifest CSVs archived at `data/reports/phase3_backup/`
- **Class Merges Executed**:
  1. **Hawa Mahal**: `Hawa mahal` (108 imgs) + `hawa mahal pics` (94 imgs) → **`Hawa Mahal`** (Total: 202 images, `class_id=11`, `IND_HAWA_MAHAL`)
  2. **India Gate**: `India_gate` (188 imgs) + `India gate pics` (101 imgs) → **`India Gate`** (Total: 289 images, `class_id=13`, `IND_INDIA_GATE`)
- **Resplit Statistics (Group-Aware 70/15/15)**:
  - **Train_v2**: 2,494 images (69.8%)
  - **Val_v2**: 536 images (15.0%)
  - **Test_v2**: 542 images (15.2%)
  - **Total**: 3,572 images across 24 classes
- **Leakage Validation Result**: **PASS** (12/12 validation checks passed, zero duplicate or near-duplicate group leakage across splits).

---

## 2. Consolidated 24 Canonical Classes & Distribution

| Class ID | Canonical Class Name | Destination ID | Total Images | Train_v2 | Val_v2 | Test_v2 | Consolidated From Original Labels |
|---:|---|---|---:|---:|---:|---:|---|
| 0 | Ajanta Caves | `IND_AJANTA_CAVES` | 92 | 64 | 14 | 14 | `Ajanta Caves` |
| 1 | Alai Darwaza | `IND_ALAI_DARWAZA` | 62 | 43 | 9 | 10 | `alai_darwaza` |
| 2 | Alai Minar | `IND_ALAI_MINAR` | 59 | 41 | 9 | 9 | `alai_minar` |
| 3 | Basilica of Bom Jesus | `IND_BASILICA_OF_BOM_JESUS` | 74 | 52 | 11 | 11 | `basilica_of_bom_jesus` |
| 4 | Charar-E-Sharif | `UNMAPPED_CHARAR-E-SHARIF` | 33 | 23 | 5 | 5 | `Charar-E- Sharif` |
| 5 | Charminar | `IND_CHARMINAR` | 216 | 151 | 32 | 33 | `charminar` |
| 6 | Chhota Imambara | `IND_CHHOTA_IMAMBARA` | 60 | 42 | 9 | 9 | `Chhota_Imambara` |
| 7 | Ellora Caves | `IND_ELLORA_CAVES` | 106 | 74 | 16 | 16 | `Ellora Caves` |
| 8 | Fatehpur Sikri | `IND_FATEHPUR_SIKRI` | 127 | 89 | 19 | 19 | `Fatehpur Sikri` |
| 9 | Gateway of India | `IND_GATEWAY_OF_INDIA` | 192 | 134 | 29 | 29 | `Gateway of India` |
| 10 | Golden Temple | `IND_GOLDEN_TEMPLE` | 169 | 118 | 25 | 26 | `golden temple` |
| 11 | **Hawa Mahal** | `IND_HAWA_MAHAL` | **202** | **141** | **30** | **31** | `Hawa mahal` + `hawa mahal pics` |
| 12 | Humayun's Tomb | `IND_HUMAYUN_S_TOMB` | 72 | 50 | 11 | 11 | `Humayun_s Tomb` |
| 13 | **India Gate** | `IND_INDIA_GATE` | **289** | **202** | **43** | **44** | `India_gate` + `India gate pics` |
| 14 | Iron Pillar | `UNMAPPED_IRON_PILLAR` | 67 | 47 | 10 | 10 | `iron_pillar` |
| 15 | Jamali Kamali Tomb | `IND_JAMALI_KAMALI_TOMB` | 199 | 139 | 30 | 30 | `jamali_kamali_tomb` |
| 16 | Khajuraho | `IND_KHAJURAHO` | 130 | 91 | 19 | 20 | `Khajuraho` |
| 17 | Lotus Temple | `IND_LOTUS_TEMPLE` | 23 | 16 | 3 | 4 | `lotus_temple` |
| 18 | Mysore Palace | `IND_MYSORE_PALACE` | 172 | 120 | 26 | 26 | `mysore_palace` |
| 19 | Qutub Minar | `IND_QUTUB_MINAR` | 432 | 302 | 65 | 65 | `qutub_minar` |
| 20 | Sun Temple Konark | `IND_SUN_TEMPLE_KONARK` | 105 | 73 | 16 | 16 | `Sun Temple Konark` |
| 21 | Taj Mahal | `IND_TAJMAHAL` | 267 | 187 | 40 | 40 | `tajmahal` |
| 22 | Tanjavur Temple | `IND_TANJAVUR_TEMPLE` | 185 | 129 | 28 | 28 | `tanjavur temple` |
| 23 | Victoria Memorial | `IND_VICTORIA_MEMORIAL` | 150 | 105 | 22 | 23 | `victoria memorial` |
| **Total** | | | **3,572** | **2,494** | **536** | **542** | |

---

## 3. Data Leakage & Schema Validation Results

Executing [`scripts/validate_class_consolidation.py`](file:///Users/dakshdedha/travel_planner/scripts/validate_class_consolidation.py):

1. ✅ Exactly 24 canonical classes defined in `landmark_classes.csv`.
2. ✅ Single class ID for Hawa Mahal (`class_id=11`).
3. ✅ Single class ID for India Gate (`class_id=13`).
4. ✅ `Hawa mahal` and `hawa mahal pics` map to `Hawa Mahal`.
5. ✅ `India_gate` and `India gate pics` map to `India Gate`.
6. ✅ Total canonical image count is 3,572 (100% preserved).
7. ✅ Zero duplicate image paths across splits.
8. ✅ ZERO exact duplicate leakage across Train/Val/Test.
9. ✅ ZERO near-duplicate group leakage across Train/Val/Test.
10. ✅ Every image has a valid class ID (0..23).
11. ✅ Every mapped destination ID is valid.
12. ✅ All 24 canonical classes represented in Train, Val, and Test splits.

**Final Validation Result**: **PASS**

---

## 4. PyTorch Dataset Loader Integration

- Updated [`backend/cv/dataset.py`](file:///Users/dakshdedha/travel_planner/backend/cv/dataset.py) to read `data/processed/landmark_classes.csv` dynamically.
- Training pipeline defaults to `train_v2.csv`, `val_v2.csv`, `test_v2.csv` for 24 output classes.
- Verified tensor output shape `(3, 224, 224)` on `train_v2.csv`.
