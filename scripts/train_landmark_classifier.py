#!/usr/bin/env python3
"""
Phase 4A: Landmark Recognition Training Script (ResNet-18 Transfer Learning)
Executes two-stage transfer learning on Apple Silicon MPS hardware with class-weighted loss,
lr scheduling, early stopping, history tracking, and checkpoint saving.
"""

import os
import sys
import time
import argparse
import random
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.models as models
from torchvision.models import ResNet18_Weights

from sklearn.metrics import precision_recall_fscore_support

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import MonumentDataset, get_transforms, load_canonical_classes

PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")
REPORTS_DIR = os.path.join(ROOT_DIR, "data", "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def select_device():
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✓ Selected Device: Apple Silicon MPS (Metal Performance Shaders)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("✓ Selected Device: NVIDIA CUDA GPU")
    else:
        device = torch.device("cpu")
        print("✓ Selected Device: CPU Fallback")
    return device

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_class_weights(df_train, num_classes):
    print("\nComputing class weights exclusively from train_v2.csv...")
    counts = df_train['class_id'].value_counts().to_dict()
    total_samples = len(df_train)
    weights = np.zeros(num_classes, dtype=np.float32)
    
    for cid in range(num_classes):
        cnt = counts.get(cid, 1)
        weights[cid] = total_samples / (num_classes * cnt)
        
    weights_tensor = torch.tensor(weights, dtype=torch.float32)
    print(f"Class Weights Min: {weights.min():.2f}, Max: {weights.max():.2f}")
    return weights_tensor

def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels.data).item()
        total += images.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc

def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    total = len(all_labels)
    eval_loss = running_loss / total
    correct = np.sum(np.array(all_preds) == np.array(all_labels))
    eval_acc = correct / total

    # Precision, Recall, F1
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='macro', zero_division=0)
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted', zero_division=0)

    return eval_loss, eval_acc, macro_p, macro_r, macro_f1, weighted_f1

def main():
    parser = argparse.ArgumentParser(description="Train Landmark Classifier with ResNet-18 Transfer Learning")
    parser.add_argument("--epochs", type=int, default=15, help="Total training epochs")
    parser.add_argument("--frozen-epochs", type=int, default=3, help="Stage 1 frozen backbone epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Stage 1 learning rate for head")
    parser.add_argument("--fine-tune-lr", type=float, default=1e-4, help="Stage 2 fine-tuning learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="Weight decay")
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    print("==========================================")
    print(" PHASE 4A: LANDMARK CLASSIFIER TRAINING  ")
    print("==========================================")
    print(f"PyTorch Version: {torch.__version__}")
    device = select_device()
    set_seed(args.seed)

    # 1. Load Canonical Classes & Datasets
    df_classes, num_classes, class_to_id, id_to_class = load_canonical_classes()
    print(f"✓ Loaded {num_classes} canonical landmark classes.")

    tr_csv = os.path.join(PROCESSED_DIR, "train_v2.csv")
    va_csv = os.path.join(PROCESSED_DIR, "val_v2.csv")

    df_train = pd.read_csv(tr_csv)
    df_val = pd.read_csv(va_csv)

    print(f"Train_v2 samples: {len(df_train)}, Val_v2 samples: {len(df_val)}")

    train_ds = MonumentDataset(tr_csv, root_dir=ROOT_DIR, transform=get_transforms('train'))
    val_ds = MonumentDataset(va_csv, root_dir=ROOT_DIR, transform=get_transforms('val'))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)

    # 2. Class-Weighted Loss
    class_weights = compute_class_weights(df_train, num_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # 3. Model Setup (ResNet-18)
    print("\nBuilding ResNet-18 transfer learning model...")
    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.to(device)

    # Stage 1: Freeze Backbone
    print(f"\n--- STAGE 1: Training Classification Head (Epochs 1..{args.frozen_epochs}) ---")
    for param in model.parameters():
        param.requires_grad = False
    for param in model.fc.parameters():
        param.requires_grad = True

    optimizer = optim.AdamW(model.fc.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    history = []
    best_val_f1 = 0.0
    patience_counter = 0

    best_checkpoint_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")
    final_checkpoint_path = os.path.join(MODELS_DIR, "landmark_resnet18_final.pth")

    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        # Stage Transition Check
        if epoch == args.frozen_epochs + 1:
            print(f"\n--- STAGE 2: Unfreezing Backbone & Fine-Tuning (Epochs {epoch}..{args.epochs}) ---")
            for param in model.parameters():
                param.requires_grad = True
            optimizer = optim.AdamW(model.parameters(), lr=args.fine_tune_lr, weight_decay=args.weight_decay)
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

        ep_start = time.time()
        tr_loss, tr_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        va_loss, va_acc, va_mp, va_mr, va_mf1, va_wf1 = evaluate(model, val_loader, criterion, device)
        ep_duration = time.time() - ep_start

        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step(va_mf1)

        print(f"Epoch {epoch:02d}/{args.epochs:02d} [{ep_duration:.1f}s] - "
              f"Tr Loss: {tr_loss:.4f}, Tr Acc: {tr_acc*100:.2f}% | "
              f"Val Loss: {va_loss:.4f}, Val Acc: {va_acc*100:.2f}%, Val Macro F1: {va_mf1*100:.2f}% (LR: {current_lr:.1e})")

        history.append({
            "epoch": epoch,
            "stage": 1 if epoch <= args.frozen_epochs else 2,
            "train_loss": round(tr_loss, 4),
            "train_acc": round(tr_acc, 4),
            "val_loss": round(va_loss, 4),
            "val_acc": round(va_acc, 4),
            "val_macro_precision": round(va_mp, 4),
            "val_macro_recall": round(va_mr, 4),
            "val_macro_f1": round(va_mf1, 4),
            "val_weighted_f1": round(va_wf1, 4),
            "learning_rate": current_lr
        })

        # Save Best Checkpoint
        if va_mf1 > best_val_f1:
            best_val_f1 = va_mf1
            patience_counter = 0
            
            # Destination mapping lookup
            dest_map_path = os.path.join(REPORTS_DIR, "destination_mapping.csv")
            dest_map_dict = {}
            if os.path.exists(dest_map_path):
                df_map = pd.read_csv(dest_map_path)
                dest_map_dict = dict(zip(df_map['original_cv_name'], df_map['matched_tourism_destination']))

            checkpoint = {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "num_classes": num_classes,
                "class_names": list(df_classes['class_name']),
                "class_to_id": class_to_id,
                "id_to_class": id_to_class,
                "destination_id_map": dict(zip(df_classes['class_name'], df_classes['destination_id'])),
                "best_val_f1": best_val_f1,
                "best_val_acc": va_acc,
                "architecture": "ResNet-18",
                "hyperparameters": vars(args)
            }
            torch.save(checkpoint, best_checkpoint_path)
            print(f"  ★ New best model checkpoint saved to: {best_checkpoint_path} (Val Macro F1: {best_val_f1*100:.2f}%)")
        else:
            if epoch > args.frozen_epochs:
                patience_counter += 1
                if patience_counter >= args.patience:
                    print(f"\n⚠️  Early stopping triggered at epoch {epoch} (Patience: {args.patience})")
                    break

    total_training_time = time.time() - start_time
    print(f"\n✓ Training completed in {total_training_time/60:.2f} minutes.")

    # Save Final Checkpoint
    final_checkpoint = {
        "epoch": len(history),
        "model_state_dict": model.state_dict(),
        "num_classes": num_classes,
        "class_names": list(df_classes['class_name']),
        "class_to_id": class_to_id,
        "id_to_class": id_to_class,
        "destination_id_map": dict(zip(df_classes['class_name'], df_classes['destination_id'])),
        "final_val_f1": history[-1]['val_macro_f1'],
        "final_val_acc": history[-1]['val_acc'],
        "architecture": "ResNet-18",
        "hyperparameters": vars(args)
    }
    torch.save(final_checkpoint, final_checkpoint_path)
    print(f"✓ Saved final model checkpoint to: {final_checkpoint_path}")

    # Save History CSV
    df_hist = pd.DataFrame(history)
    hist_csv_path = os.path.join(REPORTS_DIR, "landmark_training_history.csv")
    df_hist.to_csv(hist_csv_path, index=False)
    print(f"✓ Saved training history to: {hist_csv_path}")

if __name__ == "__main__":
    main()
