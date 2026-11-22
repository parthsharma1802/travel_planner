import time
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger("smart_travel.routing_service")

class RoutingService:
    """
    OSRM (Open Source Routing Machine) Service.
    Calculates actual driving road routes, leg distances (km), driving duration (minutes/hours),
    and detailed geometry polylines ([lat, lon] points).
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.osrm_url = "http://router.project-osrm.org/route/v1/driving"
        self.headers = {
            "User-Agent": "SmartTripAI/1.0 (contact@smarttrip.ai)"
        }

    async def get_route(self, coordinates: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Calculate road route between sequential coordinate points via OSRM.

        Args:
            coordinates: List of dicts containing [{'lat': float, 'lon': float}, ...]

        Returns:
            Dict containing OSRM route data, legs, total_distance, total_duration
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinate points required for route planning.")

        # OSRM format: lon,lat;lon,lat;...
        coord_str = ";".join([f"{c['lon']},{c['lat']}" for c in coordinates])
        cache_key = coord_str
        now = time.time()

        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["data"]

        endpoint = f"{self.osrm_url}/{coord_str}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(endpoint, params=params, headers=self.headers)
                res.raise_for_status()
                data = res.json()

                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    
                    result = {
                        "status": "success",
                        "total_distance_meters": route.get("distance", 0),
                        "total_duration_seconds": route.get("duration", 0),
                        "legs": route.get("legs", []),
                        "geometry": route.get("geometry", {}).get("coordinates", [])
                    }
                    self._cache[cache_key] = {"timestamp": now, "data": result}
                    return result
            except Exception as e:
                logger.error(f"OSRM routing API call failed for {coord_str}: {e}")

        # Fallback estimation if OSRM is temporarily offline
        return self._generate_fallback_route(coordinates)

    def _generate_fallback_route(self, coordinates: List[Dict[str, float]]) -> Dict[str, Any]:
        """Haversine road estimation fallback when OSRM API is unreachable."""
        import math
        total_dist_m = 0.0
        legs = []
        full_geometry = []

        for i in range(len(coordinates) - 1):
            c1 = coordinates[i]
            c2 = coordinates[i + 1]
            
            # Haversine distance
            lat1, lon1 = math.radians(c1["lat"]), math.radians(c1["lon"])
            lat2, lon2 = math.radians(c2["lat"]), math.radians(c2["lon"])
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = 6371 * c * 1.3 # 1.3 road curvature factor
            dist_m = dist_km * 1000
            duration_s = (dist_km / 50.0) * 3600 # 50 km/h avg speed

            total_dist_m += dist_m
            
            leg_geom = [[c1["lon"], c1["lat"]], [c2["lon"], c2["lat"]]]
            full_geometry.extend(leg_geom)

            legs.append({
                "distance": dist_m,
                "duration": duration_s,
                "summary": f"Estimated road route {i+1}",
                "steps": []
            })

        return {
            "status": "success",
            "total_distance_meters": total_dist_m,
            "total_duration_seconds": total_dist_m / (50000 / 3600),
            "legs": legs,
            "geometry": full_geometry
        }

# Global singleton routing service
routing_service = RoutingService()
