from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.services.map_service import map_service

router = APIRouter(prefix="/maps", tags=["Interactive Maps & Route Planning"])

class LocationInfo(BaseModel):
    name: str
    lat: float
    lon: float
    display_name: str

class RouteLeg(BaseModel):
    from_name: str
    to_name: str
    distance_km: float
    duration_minutes: int
    duration_text: str
    geometry: List[List[float]]

class RoutePlanRequest(BaseModel):
    origin: str = Field(..., description="Starting location (e.g. 'Delhi')")
    stops: List[str] = Field(..., description="List of sequential destination stops (e.g. ['Srinagar', 'Sonamarg', 'Gulmarg'])")

class RoutePlanResponse(BaseModel):
    status: str = "success"
    origin: LocationInfo
    stops: List[LocationInfo]
    legs: List[RouteLeg]
    total_distance_km: float
    total_duration_minutes: int
    total_duration_text: str
    geometry: List[List[float]]
    google_maps_url: str

@router.post("/route", response_model=RoutePlanResponse)
async def plan_route_post(request: RoutePlanRequest):
    """
    Plan sequential road trip route from origin through stops using Nominatim + OSRM.
    Calculates exact road distance, driving duration per leg, total route time,
    and polyline geometries for Leaflet maps.
    """
    try:
        data = await map_service.plan_route(request.origin, request.stops)
        return RoutePlanResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route planning failed: {str(exc)}"
        )

@router.get("/route", response_model=RoutePlanResponse)
async def plan_route_get(
    origin: str = Query("Delhi", description="Starting location name"),
    stops: str = Query("Srinagar,Sonamarg,Gulmarg", description="Comma-separated list of destination stops")
):
    """
    GET endpoint for map route planning convenience.
    """
    try:
        stops_list = [s.strip() for s in stops.split(",") if s.strip()]
        data = await map_service.plan_route(origin, stops_list)
        return RoutePlanResponse(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route planning failed: {str(exc)}"
        )
