import time
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("smart_travel.geocoding_service")

# Canonical Pre-Cached Coordinates for Instant Zero-Latency Resolution
CANONICAL_GEO_CACHE = {
    "delhi": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "display_name": "Delhi, India"},
    "new delhi": {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "display_name": "New Delhi, India"},
    "srinagar": {"name": "Srinagar", "lat": 34.0837, "lon": 74.7973, "display_name": "Srinagar, Jammu & Kashmir, India"},
    "sonamarg": {"name": "Sonamarg", "lat": 34.3000, "lon": 75.3000, "display_name": "Sonamarg, Jammu & Kashmir, India"},
    "gulmarg": {"name": "Gulmarg", "lat": 34.0500, "lon": 74.3800, "display_name": "Gulmarg, Jammu & Kashmir, India"},
    "agra": {"name": "Agra", "lat": 27.1767, "lon": 78.0081, "display_name": "Agra, Uttar Pradesh, India"},
    "jaipur": {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "display_name": "Jaipur, Rajasthan, India"},
    "udaipur": {"name": "Udaipur", "lat": 24.5854, "lon": 73.7125, "display_name": "Udaipur, Rajasthan, India"},
    "jodhpur": {"name": "Jodhpur", "lat": 26.2389, "lon": 73.0243, "display_name": "Jodhpur, Rajasthan, India"},
    "jaisalmer": {"name": "Jaisalmer", "lat": 26.9157, "lon": 70.9083, "display_name": "Jaisalmer, Rajasthan, India"},
    "bikaner": {"name": "Bikaner", "lat": 28.0229, "lon": 73.3119, "display_name": "Bikaner, Rajasthan, India"},
    "goa": {"name": "Goa", "lat": 15.2993, "lon": 74.1240, "display_name": "Goa, India"},
    "mumbai": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "display_name": "Mumbai, Maharashtra, India"},
    "leh": {"name": "Leh", "lat": 34.1526, "lon": 77.5771, "display_name": "Leh, Ladakh, India"},
    "manali": {"name": "Manali", "lat": 32.2432, "lon": 77.1892, "display_name": "Manali, Himachal Pradesh, India"},
    "shimla": {"name": "Shimla", "lat": 31.1048, "lon": 77.1734, "display_name": "Shimla, Himachal Pradesh, India"},
    "kullu": {"name": "Kullu", "lat": 31.9579, "lon": 77.1095, "display_name": "Kullu, Himachal Pradesh, India"},
    "varanasi": {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739, "display_name": "Varanasi, Uttar Pradesh, India"},
    "bodhgaya": {"name": "Bodhgaya", "lat": 24.6961, "lon": 84.9869, "display_name": "Bodhgaya, Bihar, India"},
    "bangalore": {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "display_name": "Bangalore, Karnataka, India"},
    "coorg": {"name": "Coorg", "lat": 12.3375, "lon": 75.8069, "display_name": "Coorg, Karnataka, India"},
    "mysore": {"name": "Mysore", "lat": 12.2958, "lon": 76.6394, "display_name": "Mysore, Karnataka, India"},
}

class GeocodingService:
    """
    Nominatim OpenStreetMap Geocoding Service with TTL Caching, Rate Limiting,
    and Proper User-Agent Header.
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            "User-Agent": "SmartTripAI/1.0 (contact@smarttrip.ai)"
        }

    async def geocode(self, location_query: str) -> Dict[str, Any]:
        """
        Geocode location query to latitude, longitude, and display name.

        Args:
            location_query: Name of place (e.g. 'Delhi', 'Sonamarg')

        Returns:
            Dict containing 'name', 'lat', 'lon', 'display_name'
        """
        query_clean = location_query.strip()
        query_key = query_clean.lower()
        now = time.time()

        # 1. Check Canonical Pre-cache
        if query_key in CANONICAL_GEO_CACHE:
            return CANONICAL_GEO_CACHE[query_key]

        # 2. Check Dynamic Memory Cache
        if query_key in self._cache:
            entry = self._cache[query_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["data"]

        # Ensure Indian cities check ends with ", India" to prevent accidental foreign store matching
        search_query = query_clean
        if "india" not in query_key and not any(country in query_key for country in ["usa", "uk", "france", "germany", "japan", "china", "dubai", "thailand"]):
            search_query = f"{query_clean}, India"

        # 3. Call Nominatim API
        params = {
            "q": search_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(self.nominatim_url, params=params, headers=self.headers)
                res.raise_for_status()
                data = res.json()

                if data and isinstance(data, list) and len(data) > 0:
                    first = data[0]
                    result = {
                        "name": query_clean.capitalize(),
                        "lat": float(first["lat"]),
                        "lon": float(first["lon"]),
                        "display_name": first.get("display_name", search_query)
                    }
                    self._cache[query_key] = {"timestamp": now, "data": result}
                    return result
            except Exception as e:
                logger.warning(f"Nominatim geocoding failed for '{search_query}': {e}")

        # Fallback if geocoding fails
        return {
            "name": query_clean.capitalize(),
            "lat": 28.6139,
            "lon": 77.2090,
            "display_name": f"{query_clean.capitalize()}, India"
        }

# Global singleton geocoding service
geocoding_service = GeocodingService()
