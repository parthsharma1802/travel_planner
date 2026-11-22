#!/usr/bin/env python3
"""
Phase 4A: Test Set Evaluation & Confusion Matrix Analysis Script
Evaluates the best trained landmark classifier model on test_v2.csv (542 images).
Computes Top-1, Top-3 Accuracy, Macro/Weighted F1, generates confusion matrix PNG,
and exports detailed classification reports.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.models as models

from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import MonumentDataset, get_transforms, load_canonical_classes

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

def select_device():
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

def evaluate_test_set():
    print("==========================================")
    print(" EVALUATING BEST MODEL ON TEST_V2 SET     ")
    print("==========================================")

    best_model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    if not os.path.exists(best_model_path):
        print(f"❌ Error: Model checkpoint not found at {best_model_path}")
        print("Please train the model first using: python scripts/train_landmark_classifier.py")
        sys.exit(1)

    device = select_device()
    checkpoint = torch.load(best_model_path, map_location=device, weights_only=False)
    print(f"✓ Loaded model checkpoint from Epoch {checkpoint.get('epoch', 'N/A')}")

    df_classes, num_classes, class_to_id, id_to_class = load_canonical_classes()
    class_names = [id_to_class[i] for i in range(num_classes)]

    # Reconstruct Model Architecture
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    test_csv = os.path.join(PROCESSED_DIR, "test_v2.csv")
    test_ds = MonumentDataset(test_csv, root_dir=ROOT_DIR, transform=get_transforms('val'))
    test_loader = DataLoader(test_ds, batch_size=16, shuffle=False, num_workers=0)

    print(f"Evaluating {len(test_ds)} test images across {num_classes} classes...")

    all_preds = []
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    all_labels = np.array(all_labels)

    # Top-1 & Top-3 Accuracy
    top1_correct = np.sum(all_preds == all_labels)
    top1_acc = top1_correct / len(all_labels)

    top3_correct = 0
    for i in range(len(all_labels)):
        top3_indices = np.argsort(all_probs[i])[-3:]
        if all_labels[i] in top3_indices:
            top3_correct += 1
    top3_acc = top3_correct / len(all_labels)

    # Precision, Recall, F1
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='macro', zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted', zero_division=0)

    print("\n------------------------------------------")
    print(f"Test Top-1 Accuracy:  {top1_acc*100:.2f}%")
    print(f"Test Top-3 Accuracy:  {top3_acc*100:.2f}%")
    print(f"Test Macro F1 Score:  {macro_f1*100:.2f}%")
    print(f"Test Weighted F1:     {weighted_f1*100:.2f}%")
    print("------------------------------------------")

    # Generate Per-Class Report
    report_dict = classification_report(all_labels, all_preds, target_names=class_names, output_dict=True, zero_division=0)
    df_report = pd.DataFrame(report_dict).transpose()
    report_csv = os.path.join(REPORTS_DIR, "test_classification_report.csv")
    df_report.to_csv(report_csv)
    print(f"✓ Saved test classification report to: {report_csv}")

    # Generate 24x24 Confusion Matrix Plot
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title("24-Class Landmark Classification Confusion Matrix", fontsize=14, fontweight='bold')
    plt.xlabel("Predicted Class")
    plt.ylabel("True Class")
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()

    cm_png_path = os.path.join(REPORTS_DIR, "landmark_confusion_matrix.png")
    plt.savefig(cm_png_path, dpi=300)
    plt.close()
    print(f"✓ Saved 24x24 confusion matrix PNG to: {cm_png_path}")

    # Generate Confusion Matrix Analysis Markdown Report
    cm_analysis_path = os.path.join(REPORTS_DIR, "confusion_matrix_analysis.md")
    with open(cm_analysis_path, "w") as f:
        f.write("# Confusion Matrix Analysis Report\n\n")
        f.write("## Overall Test Performance\n")
        f.write(f"- **Top-1 Accuracy**: {top1_acc*100:.2f}%\n")
        f.write(f"- **Top-3 Accuracy**: {top3_acc*100:.2f}%\n")
        f.write(f"- **Macro F1 Score**: {macro_f1*100:.2f}%\n")
        f.write(f"- **Weighted F1 Score**: {weighted_f1*100:.2f}%\n\n")

        f.write("## Per-Class Performance Summary\n\n")
        f.write("| Class ID | Landmark Name | Precision | Recall | F1-Score | Support |\n")
        f.write("|---:|---|---:|---:|---:|---:|\n")
        for i, cname in enumerate(class_names):
            p = report_dict[cname]['precision']
            r = report_dict[cname]['recall']
            f1 = report_dict[cname]['f1-score']
            sup = int(report_dict[cname]['support'])
            f.write(f"| {i} | {cname} | {p*100:.1f}% | {r*100:.1f}% | {f1*100:.1f}% | {sup} |\n")

    print(f"✓ Saved confusion matrix analysis MD to: {cm_analysis_path}")

if __name__ == "__main__":
    evaluate_test_set()
