from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from backend.services.weather_service import weather_service, WeatherReport

router = APIRouter(prefix="/weather", tags=["Weather Service"])

@router.get("", response_model=WeatherReport)
async def get_weather(
    city: str = Query(..., description="Destination city name (e.g., Agra, Delhi, Jaipur, Goa)")
):
    """
    Fetch current weather and 1-day forecast for a destination using Open-Meteo API.
    Features:
    - Automatic city geocoding
    - TTL Caching (10 mins)
    - Normalized response structure
    - Open-Meteo attribution compliance
    """
    try:
        data = await weather_service.get_weather_for_city(city)
        return WeatherReport(**data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve weather for {city}: {str(exc)}"
        )
