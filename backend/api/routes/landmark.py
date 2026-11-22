import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.services.landmark_service import landmark_service
from backend.services.visual_similarity_service import visual_similarity_service

logger = logging.getLogger("smart_travel.api.landmark")

router = APIRouter(prefix="/landmark", tags=["Landmark Recognition & Visual Similarity"])

# Max allowed image size: 15MB
MAX_FILE_SIZE = 15 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp", "image/gif"}


class LandmarkCandidate(BaseModel):
    rank: int
    class_name: str
    confidence_score: float
    confidence_pct: float
    class_id: int
    destination_id: Optional[str] = None


class SimilarLandmarkMatch(BaseModel):
    landmark_name: str
    location: Optional[str] = None
    similarity_score: float = Field(..., description="Cosine similarity score [0.0 - 1.0]")
    max_similarity: Optional[float] = None
    category: Optional[str] = None
    destination_id: Optional[str] = None


class TourismKnowledgeRecord(BaseModel):
    destination_id: Optional[str] = None
    destination_name: Optional[str] = None
    state: Optional[str] = None
    city_district: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[float] = None
    price_info: Optional[str] = None
    ideal_seasonality: Optional[str] = None
    description: Optional[str] = None


class LandmarkRecognitionResponse(BaseModel):
    status: str = "success"
    landmark_name: Optional[str] = Field(None, description="Confidently recognized landmark name")
    location: Optional[str] = Field(None, description="City / State location of landmark")
    confidence_level: str = Field(..., description="'high', 'moderate', or 'low'")
    confidence_score: float = Field(..., description="Top candidate probability score [0.0 - 1.0]")
    identification_status: str = Field(..., description="'confident', 'uncertain', or 'unconfident'")
    summary_statement: str = Field(..., description="Human-friendly summary phrase")
    top_predictions: List[LandmarkCandidate] = Field(default_factory=list)
    similar_landmarks: List[Dict[str, Any]] = Field(default_factory=list, description="Top visually similar monuments from FAISS similarity index")
    tourism_info: Optional[TourismKnowledgeRecord] = None
    canonical_class_id: Optional[int] = None
    embedding_compatible: bool = True
    scene_context: Optional[Dict[str, Any]] = Field(None, description="Places365 scene recognition context")


class VisualSimilaritySearchResponse(BaseModel):
    status: str = "success"
    total_matches: int
    top_matches: List[Dict[str, Any]] = Field(default_factory=list)
    distinct_landmarks: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/recognize", response_model=LandmarkRecognitionResponse)
async def recognize_landmark(
    file: UploadFile = File(..., description="Travel or monument photo for AI Landmark Recognition & FAISS Visual Similarity")
):
    """
    Recognize Indian landmark from an uploaded image using trained ResNet-18 model + FAISS Visual Similarity.
    Combines classifier predictions, visual nearest neighbors, Places365 scene context, and Tourism Knowledge Layer details.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided for landmark recognition."
        )

    # Validate content type
    content_type = file.content_type or ""
    if content_type.lower() not in ALLOWED_CONTENT_TYPES and not file.filename.lower().endswith(
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
                detail="Uploaded file is empty. Please select a valid photo."
            )

        result = landmark_service.predict(contents)

        # Attach Places365 scene recognition as supporting signal
        try:
            from backend.services.scene_service import scene_service
            scene_res = scene_service.recognize_scene(contents, top_k=3)
            if scene_res.get("status") == "success":
                result["scene_context"] = {
                    "scene": scene_res.get("scene"),
                    "display_name": scene_res.get("display_name"),
                    "travel_category": scene_res.get("travel_category"),
                    "confidence": scene_res.get("confidence")
                }
        except Exception as s_err:
            logger.debug(f"Scene recognition supporting signal skipped: {s_err}")

        return LandmarkRecognitionResponse(**result)

    except HTTPException:
        raise
    except ValueError as val_err:
        logger.warning(f"Image decoding/validation failed: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to process image: {str(val_err)}"
        )
    except Exception as exc:
        logger.error(f"Unexpected error during landmark recognition: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Landmark recognition service encountered an internal error. Please try again."
        )


@router.post("/similar", response_model=VisualSimilaritySearchResponse)
async def search_similar_landmarks(
    file: UploadFile = File(..., description="Travel or monument photo for FAISS Visual Similarity Search"),
    top_k: int = Query(6, ge=1, le=20, description="Number of nearest visual matches to retrieve")
):
    """
    Direct FAISS Visual Similarity Search.
    Extracts 512D ResNet-18 embeddings and queries monuments.index for nearest visually similar destinations.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided for visual similarity search."
        )

    content_type = file.content_type or ""
    if content_type.lower() not in ALLOWED_CONTENT_TYPES and not file.filename.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file format '{content_type}'."
        )

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image file exceeds 15MB limit."
            )

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        res = visual_similarity_service.search_similar(contents, top_k=top_k)
        return VisualSimilaritySearchResponse(**res)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Visual similarity search error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Visual similarity search encountered an internal error."
        )
