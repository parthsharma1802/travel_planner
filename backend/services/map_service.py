import logging
from typing import List, Dict, Any, Optional
import urllib.parse
from backend.services.geocoding_service import geocoding_service
from backend.services.routing_service import routing_service

logger = logging.getLogger("smart_travel.map_service")

class MapService:
    """
    High-level Map & Itinerary Route Planner Service.
    Combines Nominatim Geocoding + OSRM Road Routing + External Google Maps Navigation URLs.
    """

    async def plan_route(self, origin: str, stops: List[str]) -> Dict[str, Any]:
        """
        Plan sequential road trip route from origin through stops.

        Args:
            origin: Starting location (e.g. 'Delhi')
            stops: List of destination stops (e.g. ['Srinagar', 'Sonamarg', 'Gulmarg'])

        Returns:
            Normalized route plan dictionary
        """
        if not origin:
            origin = "Delhi"
        if not stops:
            stops = ["Agra"]

        # 1. Geocode all locations sequentially
        all_location_names = [origin] + stops
        resolved_locations = []

        for name in all_location_names:
            geo_info = await geocoding_service.geocode(name)
            resolved_locations.append(geo_info)

        origin_info = resolved_locations[0]
        stops_info = resolved_locations[1:]

        # 2. Get OSRM Road Route
        coord_list = [{"lat": loc["lat"], "lon": loc["lon"]} for loc in resolved_locations]
        osrm_data = await routing_service.get_route(coord_list)

        raw_legs = osrm_data.get("legs", [])
        raw_geometry = osrm_data.get("geometry", [])

        # Convert OSRM GeoJSON geometry [lon, lat] -> Leaflet standard [lat, lon]
        polyline_geometry = [[pt[1], pt[0]] for pt in raw_geometry]

        # 3. Format Route Legs
        legs = []
        total_dist_km = 0.0
        total_dur_min = 0.0

        for idx, leg_data in enumerate(raw_legs):
            from_loc = resolved_locations[idx]
            to_loc = resolved_locations[idx + 1]

            dist_km = round(leg_data.get("distance", 0) / 1000.0, 1)
            dur_min = round(leg_data.get("duration", 0) / 60.0)

            total_dist_km += dist_km
            total_dur_min += dur_min

            # Format duration text (e.g. "15 hrs 20 mins" or "45 mins")
            dur_hours = dur_min // 60
            dur_rem_min = dur_min % 60
            if dur_hours > 0:
                dur_text = f"{dur_hours} hrs {dur_rem_min} mins"
            else:
                dur_text = f"{dur_min} mins"

            # Create leg geometry slice
            leg_polyline = [
                [from_loc["lat"], from_loc["lon"]],
                [to_loc["lat"], to_loc["lon"]]
            ]

            legs.append({
                "from_name": from_loc["name"],
                "to_name": to_loc["name"],
                "distance_km": dist_km,
                "duration_minutes": dur_min,
                "duration_text": dur_text,
                "geometry": leg_polyline
            })

        # Format Total Duration Text
        tot_hours = int(total_dur_min // 60)
        tot_mins = int(total_dur_min % 60)
        if tot_hours > 0:
            total_dur_text = f"{tot_hours} hrs {tot_mins} mins"
        else:
            total_dur_text = f"{tot_mins} mins"

        # 4. Build External Google Maps Navigation URL (Zero API key required!)
        # Format: https://www.google.com/maps/dir/?api=1&origin=Origin&destination=FinalStop&waypoints=Stop1|Stop2
        gmaps_origin = urllib.parse.quote(origin_info["display_name"])
        gmaps_dest = urllib.parse.quote(stops_info[-1]["display_name"])
        
        waypoints_str = ""
        if len(stops_info) > 1:
            waypoint_names = [s["display_name"] for s in stops_info[:-1]]
            waypoints_str = "&waypoints=" + urllib.parse.quote("|".join(waypoint_names))

        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={gmaps_origin}&destination={gmaps_dest}{waypoints_str}"

        return {
            "status": "success",
            "origin": origin_info,
            "stops": stops_info,
            "legs": legs,
            "total_distance_km": round(total_dist_km, 1),
            "total_duration_minutes": int(total_dur_min),
            "total_duration_text": total_dur_text,
            "geometry": polyline_geometry,
            "google_maps_url": google_maps_url
        }

# Global singleton map service
map_service = MapService()
