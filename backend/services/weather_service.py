import time
import logging
from typing import Dict, Any, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger("smart_travel.weather_service")

# WMO Weather Code Interpretation Table
WMO_WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow ❄️",
    73: "Moderate snow ❄️",
    75: "Heavy snow ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌦️",
    82: "Violent rain showers ⛈️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

# Known Canonical Coordinates for Major Indian Tourism Destinations (Fast Pre-cache)
CANONICAL_COORDINATES = {
    "agra": {"lat": 27.1767, "lon": 78.0081, "name": "Agra", "country": "India"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "name": "Delhi", "country": "India"},
    "new delhi": {"lat": 28.6139, "lon": 77.2090, "name": "New Delhi", "country": "India"},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "name": "Jaipur", "country": "India"},
    "goa": {"lat": 15.2993, "lon": 74.1240, "name": "Goa", "country": "India"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai", "country": "India"},
    "varanasi": {"lat": 25.3176, "lon": 82.9739, "name": "Varanasi", "country": "India"},
    "udaipur": {"lat": 24.5854, "lon": 73.7125, "name": "Udaipur", "country": "India"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "name": "Shimla", "country": "India"},
    "manali": {"lat": 32.2432, "lon": 77.1892, "name": "Manali", "country": "India"},
}

class WeatherReport(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    current_temperature_c: float
    windspeed_kmh: float
    weather_condition: str
    today_max_temp_c: Optional[float] = None
    today_min_temp_c: Optional[float] = None
    precipitation_sum_mm: Optional[float] = None
    attribution: str = "Weather data provided by Open-Meteo.com (https://open-meteo.com/)"
    cached: bool = False

class WeatherService:
    """
    Reusable Weather Service connecting to Open-Meteo API.
    Features:
    - Geocoding resolution (City -> Lat/Lon)
    - Current weather & 1-day forecast retrieval
    - In-memory TTL Caching (10 mins)
    - Graceful error fallback
    - Open-Meteo attribution compliance
    """

    def __init__(self, cache_ttl_seconds: int = 600):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"

    async def geocode_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Resolve city name to latitude and longitude using Open-Meteo Geocoding API."""
        key = city_name.strip().lower()
        if key in CANONICAL_COORDINATES:
            return CANONICAL_COORDINATES[key]

        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(self.geocoding_url, params=params)
                res.raise_for_status()
                data = res.json()
                results = data.get("results", [])
                if results:
                    first = results[0]
                    return {
                        "lat": first.get("latitude"),
                        "lon": first.get("longitude"),
                        "name": first.get("name", city_name),
                        "country": first.get("country", "")
                    }
            except Exception as e:
                logger.warning(f"Geocoding failed for {city_name}: {e}")
        return None

    async def get_weather_for_city(self, city_name: str) -> Dict[str, Any]:
        """
        Fetch normalized current weather & forecast for a city name.
        Uses TTL caching.
        """
        cache_key = city_name.strip().lower()
        now = time.time()

        # Check Cache
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                cached_data = dict(entry["data"])
                cached_data["cached"] = True
                return cached_data

        # Resolve Geocoding
        geo = await self.geocode_city(city_name)
        if not geo:
            return self._fallback_weather(city_name)

        lat, lon = geo["lat"], geo["lon"]

        # Fetch Weather from Open-Meteo
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(self.forecast_url, params=params)
                res.raise_for_status()
                data = res.json()

                current = data.get("current_weather", {})
                daily = data.get("daily", {})

                w_code = current.get("weathercode", 0)
                condition = WMO_WEATHER_CODES.get(w_code, "Clear ☀️")

                max_temp = daily.get("temperature_2m_max", [None])[0]
                min_temp = daily.get("temperature_2m_min", [None])[0]
                precip = daily.get("precipitation_sum", [0.0])[0]

                report = {
                    "city": geo["name"],
                    "country": geo["country"],
                    "latitude": lat,
                    "longitude": lon,
                    "current_temperature_c": current.get("temperature", 25.0),
                    "windspeed_kmh": current.get("windspeed", 10.0),
                    "weather_condition": condition,
                    "today_max_temp_c": max_temp,
                    "today_min_temp_c": min_temp,
                    "precipitation_sum_mm": precip,
                    "attribution": "Weather data provided by Open-Meteo.com (https://open-meteo.com/)",
                    "cached": False
                }

                # Save to cache
                self._cache[cache_key] = {
                    "timestamp": now,
                    "data": report
                }

                return report

            except Exception as e:
                logger.error(f"Open-Meteo API request failed for {city_name}: {e}")
                return self._fallback_weather(city_name, geo)

    def _fallback_weather(self, city_name: str, geo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Safe fallback report when Open-Meteo API is unreachable."""
        return {
            "city": geo["name"] if geo else city_name.capitalize(),
            "country": geo["country"] if geo else "India",
            "latitude": geo["lat"] if geo else 27.1767,
            "longitude": geo["lon"] if geo else 78.0081,
            "current_temperature_c": 28.0,
            "windspeed_kmh": 12.0,
            "weather_condition": "Pleasant & Clear 🌤️",
            "today_max_temp_c": 32.0,
            "today_min_temp_c": 20.0,
            "precipitation_sum_mm": 0.0,
            "attribution": "Weather data provided by Open-Meteo.com (https://open-meteo.com/)",
            "cached": False,
            "fallback_used": True
        }

    async def evaluate_travel_weather(
        self,
        destination: str,
        dates_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate weather & seasonal suitability for a destination and travel period.
        Acts as a decision-support signal combining Open-Meteo live data and regional climate patterns.
        """
        dest_clean = destination.strip()
        dest_lower = dest_clean.lower()
        dates_clean = (dates_text or "").strip().lower()

        # 1. Parse Month / Season from Dates Text
        month_found = None
        months_map = {
            "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
            "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
            "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
            "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12
        }
        for m_name, m_num in months_map.items():
            if m_name in dates_clean:
                month_found = m_num
                break

        if not month_found:
            # Check for generic seasonal terms
            if any(k in dates_clean for k in ["winter", "december", "january", "sardi", "thand"]):
                month_found = 12
            elif any(k in dates_clean for k in ["monsoon", "rain", "barish", "july", "august"]):
                month_found = 7
            elif any(k in dates_clean for k in ["summer", "may", "june", "garmi"]):
                month_found = 5
            elif any(k in dates_clean for k in ["autumn", "october", "november", "diwali"]):
                month_found = 10
            elif any(k in dates_clean for k in ["spring", "march", "april", "holi"]):
                month_found = 3
            else:
                import datetime
                month_found = datetime.datetime.now().month

        # 2. Regional Climate Evaluation
        is_himalayan = any(k in dest_lower for k in [
            "uttarakhand", "himachal", "kashmir", "ladakh", "sikkim", "mussoorie",
            "nainital", "rishikesh", "haridwar", "auli", "manali", "shimla", "dharamshala",
            "spiti", "leh", "gulmarg", "sonamarg", "pahalgam", "srinagar", "gangtok", "darjeeling"
        ])
        is_desert = any(k in dest_lower for k in [
            "rajasthan", "gujarat", "jaipur", "udaipur", "jodhpur", "jaisalmer",
            "bikaner", "kutch", "pushkar", "osian", "ranthambore"
        ])
        is_coastal_south = any(k in dest_lower for k in [
            "goa", "kerala", "gokarna", "kochi", "alleppey", "munnar", "varkala",
            "andaman", "pondicherry", "ooty", "kodaikanal", "coorg", "wayanad", "karnataka"
        ])
        is_northeast = any(k in dest_lower for k in [
            "meghalaya", "shillong", "cherrapunji", "assam", "kaziranga", "arunachal", "tawang"
        ])

        season_name = "Pleasant Season"
        suitability = "favorable"
        climate_summary = ""
        outdoor_nuances = ""
        suggested_alts = []

        if is_himalayan:
            if month_found in [7, 8]:
                season_name = "Monsoon Season"
                suitability = "caution"
                climate_summary = "Lush green mountain valleys, but frequent monsoon rainfall with possible highway road closures or landslides."
                outdoor_nuances = "High humidity and rain; caution on winding hill highways. Great for offbeat valley stays, but risky for high-altitude trekking."
                suggested_alts = ["Ladakh", "Spiti Valley"]
            elif month_found in [9, 10]:
                season_name = "Post-Monsoon / Autumn"
                suitability = "favorable"
                climate_summary = "Crisp mountain air, clear panoramic Himalayan views, pleasant daytime (16–24°C) and cooler evenings (8–14°C)."
                outdoor_nuances = "Superb for sightseeing, lake towns (Nainital), yoga hubs (Rishikesh) and hill drives. Note: High-altitude flower valleys (like Valley of Flowers) begin closing around mid-October."
                suggested_alts = ["Himachal Pradesh (Solang, Kangra)", "Kashmir (Pahalgam, Gulmarg)"]
            elif month_found in [11, 12, 1, 2]:
                season_name = "Winter & Snow Season"
                suitability = "favorable"
                climate_summary = "Cold winter climate (2–12°C, subzero at night) with snowfall in higher reaches like Auli, Solang, and Gulmarg."
                outdoor_nuances = "Ideal for snow lovers and ski enthusiasts. Require heavy woolens and snow-ready transport."
                suggested_alts = ["Gulmarg (Kashmir)", "Auli (Uttarakhand)", "Manali (Himachal)"]
            else: # 3, 4, 5, 6
                season_name = "Spring / Summer"
                suitability = "favorable"
                climate_summary = "Pleasant mountain weather (15–28°C), clear sunny days, escaping the plains heat."
                outdoor_nuances = "Peak season for all sightseeing, rafting, and valley trails."
                suggested_alts = ["Himachal Pradesh", "Sikkim"]

        elif is_desert:
            if month_found in [4, 5, 6]:
                season_name = "Peak Summer"
                suitability = "caution"
                climate_summary = "High desert temperatures exceeding 38–43°C with strong afternoon sun."
                outdoor_nuances = "Sightseeing is best early morning or late evening. For cooler experiences, hill stations like Mount Abu or Udaipur lakefronts are preferred."
                suggested_alts = ["Mount Abu", "Udaipur"]
            elif month_found in [10, 11, 12, 1, 2, 3]:
                season_name = "Pleasant Winter & Cultural Season"
                suitability = "favorable"
                climate_summary = "Sunny, pleasant days (20–28°C) with brisk, cool desert nights (8–14°C)."
                outdoor_nuances = "Prime time for desert safaris, fort explorations, camping under the stars, and cultural festivals."
                suggested_alts = ["Jaisalmer Dunes", "Udaipur Lakes", "Rann of Kutch"]
            else: # 7, 8, 9
                season_name = "Monsoon Oasis"
                suitability = "favorable"
                climate_summary = "Mild showers bringing lush greenery to the Aravalli hills and lakes (26–32°C)."
                outdoor_nuances = "Scenic time for Udaipur, Kumbhalgarh, and Mount Abu."
                suggested_alts = ["Udaipur", "Kumbhalgarh"]

        elif is_coastal_south:
            if month_found in [6, 7, 8]:
                season_name = "Southwest Monsoon"
                suitability = "moderate"
                climate_summary = "Heavy tropical rains and roaring Western Ghats waterfalls, rough ocean seas."
                outdoor_nuances = "Great for Ayurvedic retreats and lush hill stations (Munnar, Coorg, Wayanad), but swimming/water sports on beaches are restricted."
                suggested_alts = ["Munnar (Kerala)", "Coorg (Karnataka)"]
            elif month_found in [10, 11, 12, 1, 2]:
                season_name = "Prime Coastal & Beach Season"
                suitability = "favorable"
                climate_summary = "Gentle sea breeze, warm sunny days (26–31°C), and calm turquoise waters."
                outdoor_nuances = "Ideal for beaches, water sports, backwaters, and island hopping."
                suggested_alts = ["Goa", "Varkala (Kerala)", "Havelock Island (Andamans)"]
            else:
                season_name = "Warm Summer"
                suitability = "favorable"
                climate_summary = "Warm & humid coastal weather (28–34°C); cooler in Western Ghats hill stations."
                outdoor_nuances = "Hill retreats like Ooty, Kodaikanal, and Coorg offer pleasant escapes."
                suggested_alts = ["Ooty (Tamil Nadu)", "Kodaikanal", "Coorg"]

        else:
            season_name = "Pleasant Travel Season"
            suitability = "favorable"
            climate_summary = "Comfortable travel conditions with moderate temperatures."
            outdoor_nuances = "Good for local sightseeing, heritage exploration, and cultural landmarks."
            suggested_alts = []

        # 3. Fetch Real-Time Weather via Open-Meteo for live context
        live_weather = None
        try:
            live_weather = await self.get_weather_for_city(dest_clean)
        except Exception as w_err:
            logger.debug(f"Live weather fetch skipped for {dest_clean}: {w_err}")

        return {
            "destination": dest_clean,
            "dates_text": dates_text,
            "month": month_found,
            "season_name": season_name,
            "suitability": suitability,
            "climate_summary": climate_summary,
            "outdoor_nuances": outdoor_nuances,
            "suggested_alternatives": suggested_alts,
            "live_weather": live_weather
        }


# Global singleton weather service instance
weather_service = WeatherService()

