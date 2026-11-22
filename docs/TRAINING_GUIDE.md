# Smart Travel Planner - Landmark Recognition Training Guide

This guide provides step-by-step instructions to train the **24-Class Landmark Classification Model** (ResNet-18 Transfer Learning) on your **Apple Silicon M4 Mac (16 GB RAM)** using hardware acceleration (`mps`).

---

## 1. Activate Environment

Open your terminal and navigate to the project root directory:

```bash
cd /Users/dakshdedha/travel_planner
source venv/bin/activate
```

Verify that Python is using the virtual environment:
```bash
which python
```
*Expected Output:* `/Users/dakshdedha/travel_planner/venv/bin/python`

---

## 2. Verify Apple Silicon Hardware Acceleration (MPS)

Run the MPS hardware verification test:

```bash
python scripts/test_mps.py
```

*Expected Output:*
```
==========================================
    APPLE SILICON / MPS TEST SCRIPT      
==========================================
PyTorch Version: 2.8.0
CPU: AVAILABLE
MPS Built in PyTorch: True
MPS Available on OS/Hardware: True
Tensor computation on MPS successful.
------------------------------------------
MPS AVAILABLE
------------------------------------------
```

---

## 3. Run a Quick Sanity Test

Before running full training, run a 1-epoch quick test to verify data loading, model initialization, loss calculation, and checkpoint saving:

```bash
python scripts/train_landmark_classifier.py --epochs 1 --frozen-epochs 1 --batch-size 4
```

*What to expect:*
- Output line showing `✓ Selected Device: Apple Silicon MPS`
- 24 canonical classes loaded
- Epoch 1 completes in ~15-30 seconds
- Best checkpoint saved to `models/trained/landmark_resnet18_best.pth`

---

## 4. Run Full Model Training

Once the sanity test passes, run full model training:

```bash
python scripts/train_landmark_classifier.py \
  --epochs 15 \
  --frozen-epochs 3 \
  --batch-size 16 \
  --lr 0.001 \
  --fine-tune-lr 0.0001 \
  --weight-decay 0.0001 \
  --patience 5 \
  --seed 42
```

---

## 5. Monitoring Terminal Output

During training, terminal output will update after each epoch:

```
Epoch 01/15 [42.1s] - Tr Loss: 2.3674, Tr Acc: 42.18% | Val Loss: 1.3525, Val Acc: 72.95%, Val Macro F1: 67.34% (LR: 1.0e-03)
  ★ New best model checkpoint saved to: /Users/dakshdedha/travel_planner/models/trained/landmark_resnet18_best.pth (Val Macro F1: 67.34%)
```

### Metrics Explained
- **Tr Loss / Tr Acc**: Training loss and classification accuracy on augmented training set.
- **Val Loss / Val Acc**: Loss and accuracy on validation set (`val_v2.csv`).
- **Val Macro F1**: Unweighted mean F1 score across all 24 classes (primary metric for saving best checkpoint).
- **LR**: Current active learning rate.

### Troubleshooting Indicators
- **NaN Loss**: Loss displays `nan` -> Reduce learning rate (`--lr 0.0001`).
- **Out of Memory (OOM)**: System runs out of memory -> Reduce batch size (`--batch-size 8`).
- **Flat Accuracy**: Accuracy does not improve after Stage 2 -> Increase epochs or adjust learning rate.

---

## 6. How to Stop Training Safely

To interrupt or stop training at any time:

Press `Ctrl + C` in your terminal.

- The training loop will stop immediately.
- Your best validation model checkpoint saved up to that point at `models/trained/landmark_resnet18_best.pth` remains **intact and fully usable**!

---

## 7. Model Checkpoints & Output Files

All outputs are saved automatically:

| Output Artifact | File Path |
|---|---|
| **Best Model Checkpoint** | `models/trained/landmark_resnet18_best.pth` |
| **Final Model Checkpoint** | `models/trained/landmark_resnet18_final.pth` |
| **Epoch Metrics History** | `data/reports/landmark_training_history.csv` |
| **Test Classification Report** | `data/reports/test_classification_report.csv` |
| **Confusion Matrix Image** | `data/reports/landmark_confusion_matrix.png` |
| **Training Report** | `data/reports/PHASE_4A_TRAINING_REPORT.md` |

---

## 8. Run Test Evaluation & Inference

After training completes, run test set evaluation on `test_v2.csv`:

```bash
python scripts/evaluate_landmark_classifier.py
```

To test landmark prediction on any single image:

```bash
python scripts/predict_landmark.py --image data/processed/monuments/qutub_minar/img_0000_1.jpg
```

*Sample Output:*
```
==========================================
       LANDMARK INFERENCE PREDICTION      
==========================================
Input Image: data/processed/monuments/qutub_minar/img_0000_1.jpg

Top-3 Predictions:
 1. Qutub Minar — 98.42% confidence (class_id=19) -> Destination ID: IND_QUTUB_MINAR
 2. Alai Minar — 1.15% confidence (class_id=2) -> Destination ID: IND_ALAI_MINAR
 3. Alai Darwaza — 0.23% confidence (class_id=1) -> Destination ID: IND_ALAI_DARWAZA
```
