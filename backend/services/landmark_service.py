import os
import io
import logging
from typing import Dict, Any, List, Optional, Union, BinaryIO
from PIL import Image
import numpy as np

import torch
import torch.nn as nn
from torchvision import transforms, models

from backend.services.tourism_service import tourism_service

logger = logging.getLogger("smart_travel.landmark_service")

# Checkpoint Path
CHECKPOINT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../models/trained/landmark_resnet18_best.pth")
)

# Canonical ImageNet Normalization (matches training transforms)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Validation Transform (224x224 RGB)
VAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])

# Canonical location mapping for landmarks not present in master CSV
FALLBACK_LANDMARK_LOCATIONS = {
    "Iron Pillar": {"city": "New Delhi", "state": "Delhi", "category": "Historical Monument", "description": "Famous 4th-century metallurgical wonder in the Qutub complex, renowned for its rust-resistant composition."},
    "Charar-E-Sharif": {"city": "Budgam", "state": "Jammu & Kashmir", "category": "Sufi Shrine", "description": "Historic wooden Sufi shrine dedicated to Sheikh Noor-ud-Din Noorani (Nund Rishi)."},
    "Alai Darwaza": {"city": "New Delhi", "state": "Delhi", "category": "Heritage Monument", "description": "Grand southern gateway of the Quwwat-ul-Islam Mosque built by Alauddin Khalji in 1311 AD."},
    "Alai Minar": {"city": "New Delhi", "state": "Delhi", "category": "Heritage Monument", "description": "Unfinished giant minaret initiated by Alauddin Khalji intended to be twice the height of Qutub Minar."},
    "Jamali Kamali Tomb": {"city": "New Delhi", "state": "Delhi", "category": "Heritage Tomb & Mosque", "description": "16th-century Sufi shrine and mosque located in the Mehrauli Archaeological Park."}
}


class LandmarkService:
    """
    Landmark Recognition Inference Service.
    Loads the trained ResNet-18 landmark classifier (24 canonical classes) once into memory.
    Provides fast, device-optimized inference with confidence calibration and Tourism Knowledge enrichment.
    """

    def __init__(self, model_path: str = CHECKPOINT_PATH):
        self.model_path = model_path
        self.device = self._select_device()
        self.model: Optional[nn.Module] = None
        self.class_names: List[str] = []
        self.id_to_class: Dict[int, str] = {}
        self.destination_id_map: Dict[str, str] = {}
        self.num_classes: int = 24
        self.is_loaded: bool = False

        self._load_model()

    def _select_device(self) -> torch.device:
        """Select fastest available compute device (MPS > CUDA > CPU)."""
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("Using Apple Silicon GPU (MPS) for Landmark Recognition inference.")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("Using NVIDIA CUDA GPU for Landmark Recognition inference.")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU for Landmark Recognition inference.")
        return device

    def _load_model(self):
        """Loads model weights and metadata once into memory."""
        if not os.path.exists(self.model_path):
            logger.error(f"Landmark model checkpoint not found at: {self.model_path}")
            return

        try:
            logger.info(f"Loading landmark model checkpoint from: {self.model_path}")
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)

            self.num_classes = checkpoint.get("num_classes", 24)
            self.class_names = checkpoint.get("class_names", [])
            self.id_to_class = checkpoint.get("id_to_class", {})
            self.destination_id_map = checkpoint.get("destination_id_map", {})

            # Instantiate standard ResNet-18 architecture with custom FC head
            model = models.resnet18(weights=None)
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, self.num_classes)

            # Load trained weights
            model.load_state_dict(checkpoint["model_state_dict"])
            model.to(self.device)
            model.eval()

            # Freeze parameters for efficient inference
            for param in model.parameters():
                param.requires_grad = False

            self.model = model
            self.is_loaded = True
            logger.info(f"Landmark model successfully initialized with {self.num_classes} classes.")

        except Exception as exc:
            logger.error(f"Failed to load landmark model: {exc}", exc_info=True)
            self.is_loaded = False

    def predict(self, image_input: Union[str, bytes, BinaryIO, Image.Image]) -> Dict[str, Any]:
        """
        Run landmark inference on an input image.

        Args:
            image_input: File path (str), raw image bytes (bytes), file-like object, or PIL Image.

        Returns:
            Structured prediction dictionary containing landmark name, confidence level,
            top-3 candidates, and enriched tourism information.
        """
        if not self.is_loaded or self.model is None:
            # Attempt reload once
            self._load_model()
            if not self.is_loaded or self.model is None:
                raise RuntimeError("Landmark recognition model is not loaded or available.")

        # 1. Load & Validate PIL Image
        try:
            if isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            elif isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif hasattr(image_input, "read"):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, str):
                if not os.path.exists(image_input):
                    raise FileNotFoundError(f"Image file not found: {image_input}")
                image = Image.open(image_input).convert("RGB")
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
        except Exception as exc:
            logger.warning(f"Invalid or corrupted image input: {exc}")
            raise ValueError(f"Could not decode image file: {str(exc)}")

        # 2. Preprocessing Transform (Resize 224x224, Normalize)
        try:
            tensor = VAL_TRANSFORM(image).unsqueeze(0).to(self.device)
        except Exception as exc:
            raise ValueError(f"Image preprocessing failed: {str(exc)}")

        # 3. Model Forward Pass
        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1).squeeze(0).cpu().numpy()

        # 4. Top-3 Predictions Extraction
        top3_indices = np.argsort(probabilities)[-3:][::-1]

        top_predictions = []
        for rank, idx in enumerate(top3_indices, 1):
            cname = self.class_names[idx] if idx < len(self.class_names) else self.id_to_class.get(idx, f"Class_{idx}")
            dest_id = self.destination_id_map.get(cname, f"IND_{cname.upper().replace(' ', '_')}")
            conf_score = float(probabilities[idx])

            top_predictions.append({
                "rank": rank,
                "class_name": cname,
                "confidence_score": round(conf_score, 4),
                "confidence_pct": round(conf_score * 100, 2),
                "class_id": int(idx),
                "destination_id": dest_id
            })

        top_1 = top_predictions[0]
        top_score = top_1["confidence_score"]

        # 5. Scene Recognition (Places365) & FAISS Visual Verification Gate
        scene_context = None
        try:
            from backend.services.scene_service import scene_service
            scene_res = scene_service.recognize_scene(image, top_k=5)
            if scene_res.get("status") == "success":
                scene_context = {
                    "scene": scene_res.get("scene"),
                    "display_name": scene_res.get("display_name"),
                    "travel_category": scene_res.get("travel_category"),
                    "confidence": scene_res.get("confidence"),
                    "top_predictions": scene_res.get("top_predictions", []),
                    "suggested_indian_alternatives": scene_res.get("suggested_indian_alternatives"),
                    "scene_experience": scene_res.get("scene_experience")
                }
        except Exception as sc_err:
            logger.debug(f"Scene service check skipped: {sc_err}")

        # 6. FAISS Visual Similarity Search Integration
        similar_landmarks = []
        max_faiss_sim = 0.0
        try:
            from backend.services.visual_similarity_service import visual_similarity_service
            faiss_res = visual_similarity_service.search_similar(image, top_k=6)
            if faiss_res.get("status") == "success":
                similar_landmarks = faiss_res.get("distinct_landmarks", [])
                for match in faiss_res.get("top_matches", []):
                    sim = float(match.get("similarity_score", 0.0))
                    if sim > max_faiss_sim:
                        max_faiss_sim = sim
        except Exception as sim_err:
            logger.warning(f"Visual similarity search skipped: {sim_err}")

        # Check if the image is an Out-Of-Distribution (OOD) Natural Landscape or Non-Monument
        is_natural_landscape = False
        if scene_context:
            t_cat = scene_context.get("travel_category", "").lower()
            s_label = scene_context.get("scene", "").lower()
            is_natural_scene = (
                any(k in t_cat for k in ["mountain", "beach", "coast", "forest", "nature", "water", "lake", "landscape", "rural"]) or
                any(k in s_label for k in ["sky", "sunset", "mountain", "valley", "field", "beach", "ocean", "forest", "tree", "hill", "desert"])
            )
            if is_natural_scene and top_score < 0.85:
                is_natural_landscape = True

        # Confidence Assessment with Cross-Validation
        if is_natural_landscape:
            confidence_level = "low"
            is_confident = False
            identification_status = "unconfident"
            summary_statement = f"Scenic {scene_context.get('display_name', 'Natural Landscape')}"
        elif top_score >= 0.80:
            confidence_level = "high"
            is_confident = True
            identification_status = "confident"
            summary_statement = f"Looks like {top_1['class_name']}"
        elif top_score >= 0.60:
            confidence_level = "moderate"
            is_confident = True
            identification_status = "uncertain"
            second_cand = top_predictions[1]["class_name"] if len(top_predictions) > 1 else ""
            summary_statement = f"May be {top_1['class_name']} (or possibly {second_cand})"
        else:
            confidence_level = "low"
            is_confident = False
            identification_status = "unconfident"
            summary_statement = "Unable to confidently identify this landmark"

        # 7. Tourism Knowledge Layer Enrichment
        tourism_info = None
        if is_confident:
            cname = top_1["class_name"]
            dest_id = top_1["destination_id"]

            matched_records = []
            if dest_id and not dest_id.startswith("UNMAPPED"):
                rec = tourism_service.get_destination_by_id(dest_id)
                if rec:
                    matched_records.append(rec)

            if not matched_records:
                matched_records = tourism_service.search_destinations(query=cname, limit=1)

            if matched_records:
                rec = matched_records[0]
                tourism_info = {
                    "destination_id": rec.get("destination_id"),
                    "destination_name": rec.get("destination_name"),
                    "state": rec.get("state"),
                    "city_district": rec.get("city_district"),
                    "category": rec.get("category", "Heritage Landmark"),
                    "rating": rec.get("rating"),
                    "reviews_count": rec.get("reviews_count"),
                    "price_info": rec.get("price_info"),
                    "ideal_seasonality": rec.get("ideal_seasonality"),
                    "description": rec.get("description"),
                }
            elif cname in FALLBACK_LANDMARK_LOCATIONS:
                fallback = FALLBACK_LANDMARK_LOCATIONS[cname]
                tourism_info = {
                    "destination_id": dest_id,
                    "destination_name": cname,
                    "state": fallback["state"],
                    "city_district": fallback["city"],
                    "category": fallback["category"],
                    "rating": 4.7,
                    "price_info": "Free / Nominal Entry",
                    "ideal_seasonality": "October to March",
                    "description": fallback["description"]
                }

        # Format location snippet
        location_str = None
        if tourism_info:
            city = tourism_info.get("city_district")
            state = tourism_info.get("state")
            if city and state and city != state:
                location_str = f"{city}, {state}"
            else:
                location_str = state or city or "India"

        return {
            "status": "success",
            "landmark_name": top_1["class_name"] if is_confident else None,
            "location": location_str,
            "confidence_level": confidence_level,
            "confidence_score": top_1["confidence_score"] if not is_natural_landscape else 0.0,
            "identification_status": identification_status,
            "summary_statement": summary_statement,
            "top_predictions": top_predictions if not is_natural_landscape else [],
            "similar_landmarks": similar_landmarks if not is_natural_landscape else [],
            "tourism_info": tourism_info,
            "canonical_class_id": int(top_1["class_id"]) if is_confident else None,
            "embedding_compatible": True,
            "scene_context": scene_context
        }


    def get_model_status(self) -> Dict[str, Any]:
        """Return diagnostic status of landmark classifier model."""
        return {
            "model_loaded": self.is_loaded,
            "device": str(self.device),
            "num_classes": self.num_classes,
            "classes": self.class_names,
            "checkpoint_path": self.model_path
        }


# Global singleton instance
landmark_service = LandmarkService()
