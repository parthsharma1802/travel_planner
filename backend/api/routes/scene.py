import io
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
from PIL import Image

from backend.services.scene_service import scene_service

logger = logging.getLogger("smart_travel.api.scene")

router = APIRouter(prefix="/scene", tags=["Places365 Scene Recognition"])

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}


class ScenePrediction(BaseModel):
    rank: int
    label: str
    display_name: str
    confidence: float
    confidence_pct: float
    travel_category: str


class SceneRecognitionResponse(BaseModel):
    status: str = "success"
    scene: str = Field(..., description="Top predicted Places365 scene class")
    label: str = Field(..., description="Raw Places365 label")
    display_name: str = Field(..., description="Clean formatted English name")
    travel_category: str = Field(..., description="Mapped high-level travel theme (e.g. beach/coast, mountain, heritage, etc.)")
    confidence: float = Field(..., description="Top prediction probability score [0.0 - 1.0]")
    confidence_pct: float = Field(..., description="Confidence percentage [0.0 - 100.0]")
    top_predictions: List[ScenePrediction] = Field(default_factory=list, description="Top-K predicted scene categories")
    suggested_indian_alternatives: Optional[Dict[str, Any]] = Field(None, description="Optional curated Indian tourism alternatives matching this visual vibe")
    device: Optional[str] = None


@router.post("/recognize", response_model=SceneRecognitionResponse)
async def recognize_scene(
    file: UploadFile = File(..., description="Image file for Places365 scene recognition")
):
    """
    Recognize environmental scene category from an uploaded image using pretrained Places365 ResNet-18.
    Returns structured scene data, top predictions, and optional Indian travel alternatives.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided for scene recognition."
        )

    # Validate file type
    content_type = file.content_type or ""
    filename_lower = file.filename.lower()
    if content_type.lower() not in ALLOWED_CONTENT_TYPES and not filename_lower.endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file format '{content_type}'. Please upload a valid JPG, PNG, or WEBP photo."
        )

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image file size exceeds the 15MB limit. Please upload a smaller photo."
            )

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # Validate image integrity
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupt or unreadable image file. Please provide a valid photo."
            )

        # Perform scene inference
        result = scene_service.recognize_scene(contents, top_k=5)

        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Scene recognition inference encountered an error.")
            )

        return SceneRecognitionResponse(
            status="success",
            scene=result.get("scene", "unknown"),
            label=result.get("label", "unknown"),
            display_name=result.get("display_name", "Unknown"),
            travel_category=result.get("travel_category", "scenic landscape"),
            confidence=result.get("confidence", 0.0),
            confidence_pct=result.get("confidence_pct", 0.0),
            top_predictions=result.get("top_predictions", []),
            suggested_indian_alternatives=result.get("suggested_indian_alternatives"),
            device=result.get("device")
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected scene recognition error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process image for scene recognition."
        )
