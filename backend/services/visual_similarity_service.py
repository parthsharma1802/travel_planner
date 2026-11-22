import os
import sys

# Prevent OpenMP thread lock crashes & duplicate libomp conflicts on macOS Apple Silicon
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import io
import logging
from typing import Dict, Any, List, Optional, Union, BinaryIO
from PIL import Image
import numpy as np
import pandas as pd
import faiss

import torch
import torch.nn as nn
from torchvision import transforms, models

from backend.services.tourism_service import tourism_service

logger = logging.getLogger("smart_travel.visual_similarity_service")

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKPOINT_PATH = os.path.join(ROOT_DIR, "models", "trained", "landmark_resnet18_best.pth")
FAISS_INDEX_PATH = os.path.join(ROOT_DIR, "data", "embeddings", "monuments.index")
METADATA_PATH = os.path.join(ROOT_DIR, "data", "embeddings", "monument_metadata.csv")

# Validation ImageNet Transform (224x224 RGB)
VAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


class ResNet18FeatureExtractor(nn.Module):
    """
    ResNet-18 Backbone Feature Extractor (512-dim output layer with L2-normalization).
    Matches the exact embedding representation used to construct monuments.index.
    """
    def __init__(self, trained_model: nn.Module):
        super(ResNet18FeatureExtractor, self).__init__()
        # Exclude final FC layer to retain average pooling output (512-dim)
        self.features = nn.Sequential(*list(trained_model.children())[:-1])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = torch.flatten(x, 1)
        # L2 Normalization (unit hypersphere projection for cosine similarity search)
        norm = torch.norm(x, p=2, dim=1, keepdim=True)
        norm = torch.where(norm == 0, torch.ones_like(norm), norm)
        x = x / norm
        return x


class VisualSimilarityService:
    """
    FAISS Visual Similarity Search Service.
    Loads the trained 512D ResNet-18 feature extractor, FAISS index, and metadata once into memory.
    Enables instant nearest-neighbor similarity search for Indian monuments and landmarks.
    """

    def __init__(
        self,
        index_path: str = FAISS_INDEX_PATH,
        metadata_path: str = METADATA_PATH,
        model_path: str = CHECKPOINT_PATH
    ):
        self.index_path = os.path.abspath(index_path)
        self.metadata_path = os.path.abspath(metadata_path)
        self.model_path = os.path.abspath(model_path)

        self.device = self._select_device()
        self.extractor: Optional[ResNet18FeatureExtractor] = None
        self.index: Optional[faiss.Index] = None
        self.df_meta: Optional[pd.DataFrame] = None
        self.is_ready: bool = False

        self._initialize_service()

    def _select_device(self) -> torch.device:
        """Select fastest compute device (MPS > CUDA > CPU)."""
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")

    def _initialize_service(self):
        """Loads FAISS index, metadata CSV, and feature extractor once into memory."""
        try:
            # 1. Load FAISS Index
            if not os.path.exists(self.index_path):
                logger.warning(f"FAISS index file not found at: {self.index_path}")
                self.is_ready = False
                return

            logger.info(f"Loading FAISS index from {self.index_path}...")
            self.index = faiss.read_index(self.index_path)

            # 2. Load Metadata
            if not os.path.exists(self.metadata_path):
                logger.warning(f"Monument metadata file not found at: {self.metadata_path}")
                self.is_ready = False
                return

            self.df_meta = pd.read_csv(self.metadata_path)

            # 3. Load Trained Model Backbone & Initialize Feature Extractor
            if os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
                num_classes = checkpoint.get("num_classes", 24)

                full_model = models.resnet18(weights=None)
                full_model.fc = nn.Linear(full_model.fc.in_features, num_classes)
                full_model.load_state_dict(checkpoint["model_state_dict"])
                full_model.to(self.device)
                full_model.eval()

                for param in full_model.parameters():
                    param.requires_grad = False

                self.extractor = ResNet18FeatureExtractor(full_model).to(self.device)
                self.extractor.eval()
                self.is_ready = True
                logger.info(f"VisualSimilarityService initialized successfully with {self.index.ntotal} indexed vectors.")
            else:
                logger.warning(f"Model checkpoint missing at: {self.model_path}")
                self.is_ready = False

        except Exception as exc:
            logger.error(f"Failed to initialize VisualSimilarityService: {exc}", exc_info=True)
            self.is_ready = False

    def search_similar(
        self,
        image_input: Union[str, bytes, BinaryIO, Image.Image],
        top_k: int = 6
    ) -> Dict[str, Any]:
        """
        Search FAISS index for visually similar monument images.

        Args:
            image_input: File path, bytes, file-like object, or PIL Image.
            top_k: Number of nearest neighbors to retrieve.

        Returns:
            Structured dictionary with top matches, distinct similar landmarks, and tourism metadata.
        """
        if not self.is_ready or self.index is None or self.extractor is None or self.df_meta is None:
            # Attempt re-initialization once
            self._initialize_service()
            if not self.is_ready or self.index is None or self.extractor is None:
                logger.warning("FAISS visual similarity index is currently unavailable.")
                return {
                    "status": "unavailable",
                    "total_matches": 0,
                    "top_matches": [],
                    "distinct_landmarks": []
                }

        # 1. Decode Image
        try:
            if isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            elif isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif hasattr(image_input, "read"):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, str):
                if not os.path.exists(image_input):
                    raise FileNotFoundError(f"Image not found: {image_input}")
                image = Image.open(image_input).convert("RGB")
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
        except Exception as exc:
            logger.warning(f"Image decode failed in visual similarity: {exc}")
            return {
                "status": "error",
                "message": f"Could not decode image: {str(exc)}",
                "top_matches": [],
                "distinct_landmarks": []
            }

        # 2. Extract 512D Normalized Embedding
        try:
            tensor = VAL_TRANSFORM(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                query_emb = self.extractor(tensor).cpu().numpy().astype(np.float32)
        except Exception as exc:
            logger.error(f"Embedding extraction failed: {exc}")
            return {
                "status": "error",
                "message": f"Embedding extraction failed: {str(exc)}",
                "top_matches": [],
                "distinct_landmarks": []
            }

        # 3. FAISS Index Search
        try:
            k = min(top_k, self.index.ntotal)
            scores, indices = self.index.search(query_emb, k)
            scores = scores[0]
            indices = indices[0]
        except Exception as exc:
            logger.error(f"FAISS search failed: {exc}")
            return {
                "status": "error",
                "message": f"FAISS search failed: {str(exc)}",
                "top_matches": [],
                "distinct_landmarks": []
            }

        # 4. Map Results & Join Tourism Metadata
        top_matches = []
        distinct_dict: Dict[str, Dict[str, Any]] = {}

        for rank, (score, idx) in enumerate(zip(scores, indices), 1):
            if idx < 0 or idx >= len(self.df_meta):
                continue

            row = self.df_meta.iloc[idx]
            cname = str(row.get("class_name", "Unknown Landmark"))
            dest_id = str(row.get("destination_id", ""))
            img_path = str(row.get("image_path", ""))
            sim_score = round(float(score), 4)

            # Look up tourism knowledge
            tourism_info = None
            if dest_id and not dest_id.startswith("UNMAPPED"):
                rec = tourism_service.get_destination_by_id(dest_id)
                if rec:
                    tourism_info = rec

            if not tourism_info:
                t_matches = tourism_service.search_destinations(query=cname, limit=1)
                if t_matches:
                    tourism_info = t_matches[0]

            loc_str = None
            if tourism_info:
                city = tourism_info.get("city_district")
                state = tourism_info.get("state")
                loc_str = f"{city}, {state}" if (city and state and city != state) else (state or city or "India")

            match_item = {
                "rank": rank,
                "landmark_name": cname,
                "destination_id": dest_id,
                "similarity_score": sim_score,
                "location": loc_str,
                "category": tourism_info.get("category") if tourism_info else "Heritage Landmark",
                "image_path": img_path,
                "tourism_info": {
                    "destination_name": tourism_info.get("destination_name"),
                    "state": tourism_info.get("state"),
                    "city_district": tourism_info.get("city_district"),
                    "category": tourism_info.get("category"),
                    "rating": tourism_info.get("rating"),
                    "description": tourism_info.get("description")
                } if tourism_info else None
            }
            top_matches.append(match_item)

            # Aggregate distinct landmark entities
            if cname not in distinct_dict:
                distinct_dict[cname] = {
                    "landmark_name": cname,
                    "location": loc_str,
                    "max_similarity": sim_score,
                    "category": tourism_info.get("category") if tourism_info else "Heritage Landmark",
                    "destination_id": dest_id
                }
            else:
                if sim_score > distinct_dict[cname]["max_similarity"]:
                    distinct_dict[cname]["max_similarity"] = sim_score

        distinct_landmarks = sorted(
            distinct_dict.values(),
            key=lambda x: x["max_similarity"],
            reverse=True
        )

        return {
            "status": "success",
            "total_matches": len(top_matches),
            "top_matches": top_matches,
            "distinct_landmarks": distinct_landmarks
        }


    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic status of FAISS index and feature extractor."""
        return {
            "faiss_loaded": self.is_ready,
            "device": str(self.device),
            "total_vectors": self.index.ntotal if self.index is not None else 0,
            "metadata_rows": len(self.df_meta) if self.df_meta is not None else 0,
            "index_path": self.index_path
        }


# Global singleton instance
visual_similarity_service = VisualSimilarityService()
