import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.services.hotel_service import hotel_service

logger = logging.getLogger("smart_travel.api.hotels")

router = APIRouter(prefix="/hotels", tags=["Hotels & Accommodation"])


class VendorOffer(BaseModel):
    vendor: str
    price_usd: float
    tax_usd: float = 0.0
    total_usd: Optional[float] = None
    price_inr: Optional[int] = None


class HotelItem(BaseModel):
    hotel_name: str
    hotel_id: str
    city: str
    lowest_price_usd: float
    lowest_price_inr: int
    best_vendor: str
    rating: Optional[float] = 4.5
    vendor_offers: List[VendorOffer] = Field(default_factory=list)


class HotelSearchResponse(BaseModel):
    status: str = "success"
    source: str = Field(..., description="'makcorps_live' or 'curated_knowledge_layer'")
    city: str
    total_hotels: int
    hotels: List[HotelItem] = Field(default_factory=list)


@router.get("/search", response_model=HotelSearchResponse)
async def search_hotels(
    city: str = Query(..., description="Destination city name for hotel price comparison"),
    limit: int = Query(10, ge=1, le=30, description="Max number of hotels to return")
):
    """
    Search hotel rates & multi-vendor pricing across Booking.com, Hotels.com, Priceline, Agoda, Trip.com via Makcorps API.
    """
    if not city or not city.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City name is required for hotel search."
        )

    try:
        result = await hotel_service.search_hotels(city=city.strip(), limit=limit)
        return HotelSearchResponse(**result)
    except Exception as exc:
        logger.error(f"Error searching hotels for {city}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hotel data: {str(exc)}"
        )
