import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.services.train_service import train_service
from backend.services.flight_service import flight_service

logger = logging.getLogger("smart_travel.api.transport")

router = APIRouter(prefix="/transport", tags=["Transport Services (Trains & Flights)"])


# ----------------------------------------------------
# TRAIN SCHEMAS & ROUTES
# ----------------------------------------------------

class TrainSearchRequest(BaseModel):
    source: str = Field(..., description="Source station code or city (e.g. 'NDLS', 'Delhi')")
    destination: str = Field(..., description="Destination station code or city (e.g. 'JP', 'Jaipur')")
    travel_date: Optional[str] = Field(None, description="Journey date in DD-MM-YYYY or natural format ('tomorrow', 'today')")
    passengers: Optional[int] = Field(1, ge=1, le=10, description="Number of passengers")
    limit: Optional[int] = Field(15, ge=1, le=50, description="Max trains to return")


class TrainStationInfo(BaseModel):
    query: str
    station_code: Optional[str] = None
    station_name: Optional[str] = None


class TrainItem(BaseModel):
    train_number: str
    train_name: str
    departure_time: str
    arrival_time: str
    duration: str
    from_station_code: str
    from_station_name: str
    to_station_code: str
    to_station_name: str
    running_days: Optional[str] = "1111111"
    distance_km: Optional[int] = None
    halts: Optional[int] = 0


class TrainSearchResponse(BaseModel):
    status: str = Field(..., description="'success', 'no_results', 'error', 'provider_unavailable'")
    provider: str = "RailKit / IndianRailApi"
    message: Optional[str] = None
    source: TrainStationInfo
    destination: TrainStationInfo
    travel_date: Optional[str] = None
    passengers: Optional[int] = 1
    total_trains: int = 0
    trains: List[TrainItem] = Field(default_factory=list)


@router.post("/train/search", response_model=TrainSearchResponse)
async def search_trains(request: TrainSearchRequest):
    """
    Search for direct trains between source and destination stations using RailKit API / IndianRailApi.
    Returns normalized train schedules, timings, durations, and stations.
    """
    if not request.source or not request.source.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source station or city is required."
        )

    if not request.destination or not request.destination.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination station or city is required."
        )

    try:
        res = await train_service.search_trains(
            source=request.source.strip(),
            destination=request.destination.strip(),
            travel_date=request.travel_date,
            passengers=request.passengers or 1,
            limit=request.limit or 15
        )

        if res.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.get("message", "Unable to complete train search.")
            )

        return TrainSearchResponse(**res)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in train search endpoint: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal train service error."
        )


# ----------------------------------------------------
# FLIGHT SCHEMAS & ROUTES (SerpApi Google Flights)
# ----------------------------------------------------

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="Departure city or airport code (e.g. 'Delhi', 'DEL')")
    destination: str = Field(..., description="Arrival city or airport code (e.g. 'Goa', 'GOI')")
    departure_date: Optional[str] = Field(None, description="Outbound date (e.g. '15 October', '2026-10-15')")
    return_date: Optional[str] = Field(None, description="Inbound date if round-trip (optional)")
    passengers: Optional[int] = Field(1, ge=1, le=9, description="Number of adult passengers")
    currency: Optional[str] = Field("INR", description="Currency code (e.g. 'INR', 'USD')")
    limit: Optional[int] = Field(10, ge=1, le=30, description="Max flights to return")


class FlightAirportInfo(BaseModel):
    query: str
    airport_code: Optional[str] = None
    airport_name: Optional[str] = None


class FlightItem(BaseModel):
    airline: str
    flight_number: Optional[str] = ""
    departure_airport_code: str
    departure_airport_name: str
    departure_time: str
    arrival_airport_code: str
    arrival_airport_name: str
    arrival_time: str
    duration: str
    duration_minutes: Optional[int] = None
    stops: int = 0
    is_non_stop: bool = True
    layovers: List[str] = Field(default_factory=list)
    price: Optional[int] = None
    currency: str = "INR"
    travel_class: Optional[str] = "Economy"
    airplane: Optional[str] = None
    airline_logo: Optional[str] = None
    booking_token: Optional[str] = None


class FlightSearchResponse(BaseModel):
    status: str = Field(..., description="'success', 'no_results', 'error', 'provider_unavailable'")
    provider: str = "SerpApi (Google Flights)"
    message: Optional[str] = None
    origin: FlightAirportInfo
    destination: FlightAirportInfo
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    trip_type: str = "one_way"
    passengers: Optional[int] = 1
    currency: str = "INR"
    total_flights: int = 0
    flights: List[FlightItem] = Field(default_factory=list)


@router.post("/flight/search", response_model=FlightSearchResponse)
async def search_flights(request: FlightSearchRequest):
    """
    Search live Google Flights via SerpApi.
    Returns normalized flights with airlines, departure/arrival times, durations, stops, and prices.
    """
    if not request.origin or not request.origin.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Origin city or airport code is required."
        )

    if not request.destination or not request.destination.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Destination city or airport code is required."
        )

    try:
        res = await flight_service.search_flights(
            origin=request.origin.strip(),
            destination=request.destination.strip(),
            departure_date=request.departure_date,
            return_date=request.return_date,
            passengers=request.passengers or 1,
            currency=request.currency or "INR",
            limit=request.limit or 10
        )

        if res.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=res.get("message", "Unable to complete flight search.")
            )

        return FlightSearchResponse(**res)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in flight search endpoint: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal flight service error."
        )

