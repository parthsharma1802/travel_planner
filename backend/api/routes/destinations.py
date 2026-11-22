from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.services.tourism_service import tourism_service, DestinationRecord

router = APIRouter(prefix="/destinations", tags=["Tourism Dataset Knowledge Layer"])

class SearchDestinationsResponse(BaseModel):
    status: str = "success"
    count: int
    results: List[DestinationRecord]

@router.get("/search", response_model=SearchDestinationsResponse)
async def search_destinations(
    query: Optional[str] = Query(None, description="Keyword search across destination name, district, description"),
    state: Optional[str] = Query(None, description="Filter by state (e.g. Rajasthan, Goa, Uttar Pradesh)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Tourist Attraction)"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating filter"),
    limit: int = Query(5, ge=1, le=50, description="Maximum number of results to return")
):
    """
    Search and filter verified Indian tourism destinations from tourism_master.csv.
    """
    try:
        results = tourism_service.search_destinations(
            query=query,
            state=state,
            category=category,
            min_rating=min_rating,
            limit=limit
        )
        return SearchDestinationsResponse(
            status="success",
            count=len(results),
            results=[DestinationRecord(**r) for r in results]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching tourism dataset: {str(exc)}"
        )
