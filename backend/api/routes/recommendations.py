from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.recommendation.engine import recommendation_engine
from backend.services.weather_service import weather_service

router = APIRouter(prefix="/recommendations", tags=["Recommendation Engine"])

class RecommendationRequest(BaseModel):
    destination: Optional[str] = Field(None, description="Target destination city/region/state")
    starting_point: Optional[str] = Field(None, description="Starting origin city for route-aware ranking")
    experiences: Optional[List[str]] = Field(default_factory=list, description="List of user experience preferences")
    travelers: Optional[str] = Field(None, description="Traveler group type (e.g. Family, Friends, Couple, Solo)")
    budget: Optional[str] = Field(None, description="Free-text budget string (e.g. ₹50k, 20000 total)")
    transport: Optional[str] = Field(None, description="Mode of transport (Car, Train, Flight, etc.)")
    travel_style: Optional[str] = Field(None, description="Pace/style (e.g. relaxed, fast-paced, luxury)")
    weather_condition: Optional[str] = Field(None, description="Optional weather condition override")
    top_n: Optional[int] = Field(10, ge=1, le=50, description="Max number of ranked recommendations to return")

class RecommendationItem(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    type: str = "attraction"
    score: float
    priority: str
    reasons: List[str]
    lat: Optional[float] = None
    lng: Optional[float] = None
    description: Optional[str] = None
    seasonality: Optional[str] = None

class RecommendationResponse(BaseModel):
    status: str = "success"
    destination: Optional[str] = None
    origin: Optional[str] = None
    recommendations: List[RecommendationItem]
    intermediate_stops: List[str] = []
    context_summary: str
    total_candidates: int

@router.post("", response_model=RecommendationResponse)
async def get_recommendations(req: RecommendationRequest):
    try:
        trip_context = {
            "destination": req.destination,
            "starting_point": req.starting_point,
            "experiences": req.experiences or [],
            "travelers": req.travelers,
            "budget": req.budget,
            "transport": req.transport,
            "travel_style": req.travel_style,
        }

        # Auto-fetch live weather if destination is provided and weather_condition not given
        weather_cond = req.weather_condition
        if not weather_cond and req.destination:
            try:
                w_info = await weather_service.get_weather_for_city(req.destination)
                if w_info:
                    weather_cond = w_info.get("weather_condition")
            except Exception:
                pass

        result = recommendation_engine.recommend(
            trip_context=trip_context,
            weather_condition=weather_cond,
            top_n=req.top_n or 10,
        )

        return RecommendationResponse(
            status="success",
            destination=req.destination,
            origin=req.starting_point,
            recommendations=result["recommendations"],
            intermediate_stops=result.get("intermediate_stops", []),
            context_summary=result.get("context_summary", ""),
            total_candidates=result.get("total_candidates", 0),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation engine failed: {str(exc)}"
        )
