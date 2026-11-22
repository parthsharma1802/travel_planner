# PHASE 4A: LANDMARK CLASSIFIER TRAINING REPORT

**AI-Powered Visual Travel Recommendation System — Phase 4A Summary**

---

## 1. Executive Summary & Hardware Performance

- **Hardware Acceleration**: Apple Silicon MPS (Metal Performance Shaders) on M4 (16 GB RAM)
- **PyTorch / torchvision**: PyTorch 2.8.0 / torchvision 0.23.0
- **Model Architecture**: ResNet-18 Transfer Learning with 24-class Linear Head (`Linear(512, 24)`)
- **Dataset Ratios**:
  - **Train_v2**: 2,494 images across 24 canonical classes
  - **Val_v2**: 536 images across 24 canonical classes
  - **Test_v2**: 542 images across 24 canonical classes
- **Training Duration**: 7.83 minutes (10 epochs total, early stopping triggered at Epoch 10)
- **Best Validation Checkpoint**: Epoch 5 (`models/trained/landmark_resnet18_best.pth`)
- **Overall Phase 4A Status**: **PASS**

---

## 2. Key Validation & Test Metrics

| Evaluation Metric | Validation Performance (Best Epoch 5) | Test Set Performance (`test_v2.csv`) |
|---|---:|---:|
| **Top-1 Accuracy** | **96.46%** | **93.17%** |
| **Top-3 Accuracy** | N/A | **98.15%** |
| **Macro F1 Score** | **96.19%** | **93.38%** |
| **Weighted F1 Score** | 96.30% | **93.12%** |
| **Macro Precision** | 96.40% | 93.65% |
| **Macro Recall** | 96.10% | 93.42% |

---

## 3. Epoch-by-Epoch Training Log

| Epoch | Stage | Train Loss | Train Acc | Val Loss | Val Acc | Val Macro F1 | Learning Rate | Action |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | Stage 1 (Head) | 2.3674 | 42.18% | 1.3525 | 72.95% | 67.34% | $1.0 \times 10^{-3}$ | Checkpoint Saved |
| 2 | Stage 1 (Head) | 1.3048 | 72.73% | 0.9185 | 79.48% | 76.79% | $1.0 \times 10^{-3}$ | Checkpoint Saved |
| 3 | Stage 1 (Head) | 0.9379 | 79.71% | 0.7071 | 84.33% | 81.19% | $1.0 \times 10^{-3}$ | Checkpoint Saved |
| 4 | Stage 2 (Fine-Tune) | 0.3847 | 90.02% | 0.2236 | 94.22% | 92.95% | $1.0 \times 10^{-4}$ | Checkpoint Saved |
| **5** | **Stage 2 (Fine-Tune)** | **0.1203** | **96.35%** | **0.1576** | **96.46%** | **96.19%** | $1.0 \times 10^{-4}$ | **★ Best Model** |
| 6 | Stage 2 (Fine-Tune) | 0.0856 | 97.35% | 0.1745 | 95.15% | 93.28% | $1.0 \times 10^{-4}$ | - |
| 7 | Stage 2 (Fine-Tune) | 0.0542 | 98.44% | 0.2107 | 94.96% | 94.12% | $1.0 \times 10^{-4}$ | - |
| 8 | Stage 2 (Fine-Tune) | 0.0457 | 98.64% | 0.1751 | 96.08% | 95.43% | $1.0 \times 10^{-4}$ | - |
| 9 | Stage 2 (Fine-Tune) | 0.0280 | 99.16% | 0.1618 | 96.08% | 95.48% | $5.0 \times 10^{-5}$ | LR Reduced |
| 10 | Stage 2 (Fine-Tune) | 0.0214 | 99.12% | 0.1772 | 96.08% | 95.79% | $5.0 \times 10^{-5}$ | Early Stopping |

---

## 4. Inference Test Verification

Tested image: `data/processed/monuments/qutub_minar/img_3287_img378.jpg`

```
Top-3 Predictions:
 1. Qutub Minar — 99.67% — class_id=19 — IND_QUTUB_MINAR
 2. Iron Pillar — 0.16% — class_id=14 — UNMAPPED_IRON_PILLAR
 3. Gateway of India — 0.04% — class_id=9 — IND_GATEWAY_OF_INDIA
```

- **Top-1 Prediction**: Qutub Minar (**99.67% confidence**)
- **Resolved Destination ID**: `IND_QUTUB_MINAR`
- **Softmax Sum**: $0.9967 + 0.0016 + 0.0004 + \dots = 1.0000$ (100% valid probability distribution)

---

## 5. Summary of Saved Artifacts

- 📦 **Best Model Checkpoint**: `models/trained/landmark_resnet18_best.pth`
- 📦 **Final Model Checkpoint**: `models/trained/landmark_resnet18_final.pth`
- 📊 **Training History CSV**: `data/reports/landmark_training_history.csv`
- 📈 **Test Classification Report**: `data/reports/test_classification_report.csv`
- 🖼️ **Confusion Matrix Heatmap**: `data/reports/landmark_confusion_matrix.png`
- 📝 **Confusion Matrix Analysis**: `data/reports/confusion_matrix_analysis.md`
- 🐍 **Inference Script**: `scripts/predict_landmark.py`
