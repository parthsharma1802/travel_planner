"""
SmartTrip — Itinerary PDF API endpoint
POST /api/itinerary/pdf
GET /api/itinerary/{trip_id}/pdf (mock/adapter endpoint)
Accepts the itinerary + preferences payload that the frontend has in memory.
Returns a downloadable PDF (application/pdf).
"""
import logging
from io import BytesIO
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.pdf_service import generate_itinerary_pdf_async

logger = logging.getLogger("smarttrip.itinerary_api")

router = APIRouter(prefix="/itinerary", tags=["Itinerary PDF"])


class PDFRequest(BaseModel):
    itinerary: Dict[str, Any] = Field(..., description="Structured itinerary dict from chat response")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Trip preferences (origin, dest, budget…)")
    route_data: Optional[Dict[str, Any]] = Field(None, description="Optional OSRM route data")
    hotel: Optional[Dict[str, Any]] = Field(None, description="Optional selected or recommended hotel")
    flight: Optional[Dict[str, Any]] = Field(None, description="Optional selected flight")
    train: Optional[Dict[str, Any]] = Field(None, description="Optional selected train")
    weather: Optional[Dict[str, Any]] = Field(None, description="Optional destination weather")


@router.post("/pdf")
async def download_itinerary_pdf(request: PDFRequest):
    """
    Generate and return a polished, print-ready A4 PDF for the final itinerary using Gotenberg Chromium.
    Uses only verified data from chat and selected booking options with validated budget math.
    """
    if not request.itinerary or not isinstance(request.itinerary, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid itinerary data dictionary is required."
        )

    try:
        pdf_bytes = await generate_itinerary_pdf_async(
            itinerary=request.itinerary,
            preferences=request.preferences or {},
            route_data=request.route_data,
            hotel=request.hotel,
            flight=request.flight,
            train=request.train,
            weather=request.weather,
        )
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(exc)}"
        )

    overview = request.itinerary.get("overview") if isinstance(request.itinerary.get("overview"), dict) else {}
    dest = overview.get("destination") or (request.preferences or {}).get("destination") or "trip"
    title = overview.get("title") or request.itinerary.get("title") or dest
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(title))[:48]
    filename = f"Dora_AI_{safe_name}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "no-store",
        },
    )
