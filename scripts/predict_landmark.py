#!/usr/bin/env python3
"""
Phase 4A: Landmark Prediction Inference Script
Loads trained ResNet-18 checkpoint and predicts Top-3 landmark classes for a given input image.
Usage:
  python scripts/predict_landmark.py --image path/to/image.jpg
"""

import os
import sys
import argparse
from PIL import Image
import numpy as np

import torch
import torch.nn as nn
import torchvision.models as models

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.cv.dataset import get_transforms

MODELS_DIR = os.path.join(ROOT_DIR, "models", "trained")

def select_device():
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

def predict(image_path, model_path=None):
    if model_path is None:
        model_path = os.path.join(MODELS_DIR, "landmark_resnet18_best.pth")

    if not os.path.exists(model_path):
        print(f"❌ Error: Model checkpoint not found at {model_path}")
        print("Please train the model first using: python scripts/train_landmark_classifier.py")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"❌ Error: Input image not found at {image_path}")
        sys.exit(1)

    device = select_device()
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)

    num_classes = checkpoint.get("num_classes", 24)
    class_names = checkpoint.get("class_names", [])
    id_to_class = checkpoint.get("id_to_class", {})
    dest_id_map = checkpoint.get("destination_id_map", {})

    # Reconstruct Model
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    # Load & Preprocess Image
    transform = get_transforms('val')
    image = Image.open(image_path).convert('RGB')
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = torch.softmax(outputs, dim=1).squeeze(0).cpu().numpy()

    # Top-3 predictions
    top3_indices = np.argsort(probabilities)[-3:][::-1]

    results = []
    for rank, idx in enumerate(top3_indices, 1):
        cname = class_names[idx] if idx < len(class_names) else id_to_class.get(idx, f"Class_{idx}")
        dest_id = dest_id_map.get(cname, f"IND_{cname.upper()}")
        conf = float(probabilities[idx] * 100)

        results.append({
            "rank": rank,
            "class_name": cname,
            "confidence_pct": conf,
            "class_id": int(idx),
            "destination_id": dest_id
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="Predict Landmark Class for Input Image")
    parser.add_argument("--image", type=str, required=True, help="Path to input image file")
    parser.add_argument("--model", type=str, default=None, help="Path to model checkpoint")

    args = parser.parse_args()

    results = predict(args.image, args.model)

    print("==========================================")
    print("       LANDMARK INFERENCE PREDICTION      ")
    print("==========================================")
    print(f"Input Image: {args.image}\n")
    print("Top-3 Predictions:")
    for r in results:
        print(f" {r['rank']}. {r['class_name']} — {r['confidence_pct']:.2f}% — class_id={r['class_id']} — {r['destination_id']}")
    print("------------------------------------------")

if __name__ == "__main__":
    main()
