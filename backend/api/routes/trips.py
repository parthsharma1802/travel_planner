import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.services.trip_storage_service import trip_storage_service

logger = logging.getLogger("smart_travel.api.trips")

router = APIRouter(tags=["Saved Trips"])

class RenameTripRequest(BaseModel):
    title: str

class SaveTripRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    destination: Optional[str] = None
    origin: Optional[str] = None
    dates: Optional[str] = None
    duration: Optional[str] = None
    travelers: Optional[str] = None
    budget: Optional[str] = None
    transport: Optional[Dict[str, Any]] = None
    hotel: Optional[Dict[str, Any]] = None
    itinerary: Optional[Dict[str, Any]] = None
    route_data: Optional[Dict[str, Any]] = None
    estimated_total: Optional[int] = None
    notes: Optional[str] = None

@router.get("/trips")
def list_saved_trips():
    """List all saved itineraries and trips."""
    trips = trip_storage_service.list_trips()
    return {
        "status": "success",
        "total": len(trips),
        "trips": trips
    }

@router.get("/trips/{trip_id}")
def get_saved_trip(trip_id: str):
    """Retrieve a saved trip by ID."""
    trip = trip_storage_service.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found")
    return {
        "status": "success",
        "trip": trip
    }

@router.post("/trips")
def create_or_save_trip(trip_req: SaveTripRequest):
    """Save or create a new trip with complete itinerary and context."""
    trip_dict = trip_req.dict(exclude_unset=True)
    created = trip_storage_service.create_trip(trip_dict)
    return {
        "status": "success",
        "message": "Trip saved successfully",
        "trip": created
    }

@router.patch("/trips/{trip_id}/rename")
def rename_saved_trip(trip_id: str, req: RenameTripRequest):
    """Rename a saved trip."""
    updated = trip_storage_service.rename_trip(trip_id, req.title)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found or invalid title")
    return {
        "status": "success",
        "message": "Trip renamed successfully",
        "trip": updated
    }

@router.delete("/trips/{trip_id}")
def delete_saved_trip(trip_id: str):
    """Delete a saved trip."""
    deleted = trip_storage_service.delete_trip(trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Trip with ID {trip_id} not found")
    return {
        "status": "success",
        "message": f"Trip {trip_id} deleted successfully"
    }
