import os
import sys
import json
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.parse
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

logger = logging.getLogger("smart_travel.flight_service")

# Canonical Indian & Major International City / Hub to IATA Airport Code Map
CITY_TO_AIRPORT_CODE: Dict[str, str] = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "goa": "GOI",
    "dabolim": "GOI",
    "mopa": "GOX",
    "mumbai": "BOM",
    "bombay": "BOM",
    "jaipur": "JAI",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "madras": "MAA",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "ahmedabad": "AMD",
    "pune": "PNQ",
    "kochi": "COK",
    "cochin": "COK",
    "varanasi": "VNS",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "chandigarh": "IXC",
    "lucknow": "LKO",
    "udaipur": "UDR",
    "jodhpur": "JDH",
    "jaisalmer": "JSA",
    "dehradun": "DED",
    "bhopal": "BHO",
    "indore": "IDR",
    "patna": "PAT",
    "bagdogra": "IXB",
    "guwahati": "GAU",
    "port blair": "IXZ",
    "leh": "IXL",
    "dubai": "DXB",
    "singapore": "SIN",
    "bangkok": "BKK",
    "london": "LHR",
    "new york": "JFK",
}


def _resolve_airport_code(query: str) -> str:
    """Resolve a city name or IATA code to a standard 3-letter uppercase airport code."""
    if not query:
        return ""
    q = query.strip()
    # If already a 3-letter IATA uppercase code
    if re.match(r"^[A-Z]{3}$", q):
        return q.upper()

    q_lower = q.lower()
    if q_lower in CITY_TO_AIRPORT_CODE:
        return CITY_TO_AIRPORT_CODE[q_lower]

    for city, code in CITY_TO_AIRPORT_CODE.items():
        if city in q_lower or q_lower in city:
            return code

    return q.upper()


def _normalize_flight_date(date_str: Optional[str]) -> Optional[str]:
    """Convert natural/formatted date strings into YYYY-MM-DD required by Google Flights."""
    if not date_str:
        return None
    d = date_str.strip().lower()

    today = datetime.now()
    if d in ["today", "aaj"]:
        return today.strftime("%Y-%m-%d")
    elif d in ["tomorrow", "kal", "next day"]:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif d in ["day after tomorrow", "parson"]:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # Already YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return d

    # DD-MM-YYYY or DD/MM/YYYY
    m_ddmmyyyy = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", d)
    if m_ddmmyyyy:
        return f"{m_ddmmyyyy.group(3)}-{int(m_ddmmyyyy.group(2)):02d}-{int(m_ddmmyyyy.group(1)):02d}"

    # Natural month formats (e.g. '15 October', '15 Oct', 'October 15', '15th October 2026')
    month_names = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }
    m_nat1 = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)(?:\s+(\d{4}))?", d)
    if m_nat1:
        day = int(m_nat1.group(1))
        mon_str = m_nat1.group(2)[:3]
        year = int(m_nat1.group(3)) if m_nat1.group(3) else today.year
        if mon_str in month_names:
            mon = month_names[mon_str]
            return f"{year:04d}-{mon:02d}-{day:02d}"

    m_nat2 = re.search(r"([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s+(\d{4}))?", d)
    if m_nat2:
        mon_str = m_nat2.group(1)[:3]
        day = int(m_nat2.group(2))
        year = int(m_nat2.group(3)) if m_nat2.group(3) else today.year
        if mon_str in month_names:
            mon = month_names[mon_str]
            return f"{year:04d}-{mon:02d}-{day:02d}"

    return None


def _format_duration_mins(minutes: Optional[int]) -> str:
    """Format duration minutes to e.g. '2h 35m'."""
    if not minutes:
        return "N/A"
    hrs = minutes // 60
    mins = minutes % 60
    if hrs > 0 and mins > 0:
        return f"{hrs}h {mins}m"
    elif hrs > 0:
        return f"{hrs}h"
    return f"{mins}m"


class FlightService:
    """
    Google Flights Service via SerpApi.
    Provides live real-time domestic & international flight schedules, pricing, and airlines.
    """

    def __init__(self):
        self.api_key = os.environ.get("SERPAPI_API_KEY", "")

    def _get_api_key(self) -> str:
        return self.api_key or os.environ.get("SERPAPI_API_KEY", "")

    def _fetch_serpapi_sync(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute synchronous HTTP request to SerpApi."""
        query_string = urllib.parse.urlencode(params)
        url = f"https://serpapi.com/search.json?{query_string}"
        headers = {
            "User-Agent": "SmartTrip/1.5.0 (FlightService)",
            "Accept": "application/json"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read().decode("utf-8", errors="ignore")
            return json.loads(raw)

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        passengers: Optional[int] = 1,
        currency: str = "INR",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search live Google Flights via SerpApi.

        Args:
            origin: Departure city or airport code (e.g. 'Delhi' or 'DEL')
            destination: Arrival city or airport code (e.g. 'Goa' or 'GOI')
            departure_date: Outbound travel date (e.g. '15 October' or '2026-10-15')
            return_date: Inbound travel date if round-trip (optional)
            passengers: Number of adult passengers (default 1)
            currency: Currency code (default 'INR')
            limit: Max flight results to return

        Returns:
            Normalized dictionary containing flight options, airlines, durations, prices.
        """
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("SERPAPI_API_KEY is missing from environment.")
            return {
                "status": "provider_unavailable",
                "message": "SerpApi Google Flights search is not configured.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": None},
                "destination": {"query": destination, "airport_code": None},
                "departure_date": departure_date,
                "return_date": return_date,
                "trip_type": "one_way",
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        orig_code = _resolve_airport_code(origin)
        dest_code = _resolve_airport_code(destination)

        if not orig_code or not dest_code:
            return {
                "status": "error",
                "message": "Both origin and destination locations are required.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": departure_date,
                "return_date": return_date,
                "trip_type": "one_way",
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        if orig_code == dest_code:
            return {
                "status": "error",
                "message": "Origin and destination airports cannot be identical.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": departure_date,
                "return_date": return_date,
                "trip_type": "one_way",
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        norm_dep_date = _normalize_flight_date(departure_date) or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        norm_ret_date = _normalize_flight_date(return_date) if return_date else None

        trip_type = "round_trip" if norm_ret_date else "one_way"
        serp_type = "1" if norm_ret_date else "2"

        params: Dict[str, Any] = {
            "engine": "google_flights",
            "departure_id": orig_code,
            "arrival_id": dest_code,
            "outbound_date": norm_dep_date,
            "currency": currency,
            "hl": "en",
            "type": serp_type,
            "adults": max(1, min(passengers or 1, 9)),
            "api_key": api_key
        }
        if norm_ret_date:
            params["return_date"] = norm_ret_date

        try:
            loop = asyncio.get_event_loop()
            raw_payload = await loop.run_in_executor(None, self._fetch_serpapi_sync, params)
        except asyncio.TimeoutError:
            logger.warning(f"SerpApi Google Flights timed out for {orig_code} -> {dest_code}")
            return {
                "status": "timeout",
                "message": "Flight search provider timed out. Please try again.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": norm_dep_date,
                "return_date": norm_ret_date,
                "trip_type": trip_type,
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }
        except Exception as exc:
            logger.error(f"SerpApi Google Flights query failed: {exc}", exc_info=True)
            return {
                "status": "error",
                "message": "Failed to connect to flight search provider.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": norm_dep_date,
                "return_date": norm_ret_date,
                "trip_type": trip_type,
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        # Check for error in payload
        if "error" in raw_payload:
            err_msg = raw_payload.get("error", "No flights found.")
            logger.warning(f"SerpApi Google Flights returned error: {err_msg}")
            return {
                "status": "no_results" if "no flights" in err_msg.lower() else "error",
                "message": err_msg,
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": norm_dep_date,
                "return_date": norm_ret_date,
                "trip_type": trip_type,
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        raw_options = raw_payload.get("best_flights", []) + raw_payload.get("other_flights", [])
        if not raw_options:
            return {
                "status": "no_results",
                "message": f"No flights found between {orig_code} and {dest_code} on {norm_dep_date}.",
                "provider": "SerpApi (Google Flights)",
                "origin": {"query": origin, "airport_code": orig_code},
                "destination": {"query": destination, "airport_code": dest_code},
                "departure_date": norm_dep_date,
                "return_date": norm_ret_date,
                "trip_type": trip_type,
                "passengers": passengers or 1,
                "currency": currency,
                "total_flights": 0,
                "flights": []
            }

        normalized_flights = []
        for opt in raw_options[:limit]:
            legs = opt.get("flights", [])
            if not legs:
                continue

            first_leg = legs[0]
            last_leg = legs[-1]

            # Primary Airline
            airline_name = first_leg.get("airline") or "Airline"
            flight_no = first_leg.get("flight_number") or ""
            if len(legs) > 1 and last_leg.get("airline") and last_leg.get("airline") != airline_name:
                airline_name = f"{airline_name} / {last_leg.get('airline')}"

            # Times
            dep_time_raw = first_leg.get("departure_airport", {}).get("time", "")
            arr_time_raw = last_leg.get("arrival_airport", {}).get("time", "")

            # Extract HH:MM
            dep_time = dep_time_raw.split(" ")[-1] if " " in dep_time_raw else dep_time_raw
            arr_time = arr_time_raw.split(" ")[-1] if " " in arr_time_raw else arr_time_raw

            from_stn_code = first_leg.get("departure_airport", {}).get("id", orig_code)
            from_stn_name = first_leg.get("departure_airport", {}).get("name", origin)
            to_stn_code = last_leg.get("arrival_airport", {}).get("id", dest_code)
            to_stn_name = last_leg.get("arrival_airport", {}).get("name", destination)

            total_mins = opt.get("total_duration") or sum(l.get("duration", 0) for l in legs)
            duration_str = _format_duration_mins(total_mins)

            num_stops = len(legs) - 1
            layovers_list = []
            for lay in opt.get("layovers", []):
                lay_name = lay.get("name") or lay.get("id") or "Stop"
                lay_dur = _format_duration_mins(lay.get("duration"))
                layovers_list.append(f"{lay_name} ({lay_dur})")

            price_val = opt.get("price")
            travel_cls = first_leg.get("travel_class") or "Economy"
            plane = first_leg.get("airplane") or ""

            normalized_flights.append({
                "airline": airline_name,
                "flight_number": flight_no,
                "departure_airport_code": from_stn_code,
                "departure_airport_name": from_stn_name,
                "departure_time": dep_time,
                "arrival_airport_code": to_stn_code,
                "arrival_airport_name": to_stn_name,
                "arrival_time": arr_time,
                "duration": duration_str,
                "duration_minutes": total_mins,
                "stops": num_stops,
                "is_non_stop": (num_stops == 0),
                "layovers": layovers_list,
                "price": price_val,
                "currency": currency,
                "travel_class": travel_cls,
                "airplane": plane,
                "airline_logo": opt.get("airline_logo") or first_leg.get("airline_logo"),
                "booking_token": opt.get("booking_token")
            })

        return {
            "status": "success",
            "provider": "SerpApi (Google Flights)",
            "origin": {
                "query": origin,
                "airport_code": orig_code,
                "airport_name": normalized_flights[0]["departure_airport_name"] if normalized_flights else origin
            },
            "destination": {
                "query": destination,
                "airport_code": dest_code,
                "airport_name": normalized_flights[0]["arrival_airport_name"] if normalized_flights else destination
            },
            "departure_date": norm_dep_date,
            "return_date": norm_ret_date,
            "trip_type": trip_type,
            "passengers": passengers or 1,
            "currency": currency,
            "total_flights": len(normalized_flights),
            "flights": normalized_flights
        }


# Global singleton instance
flight_service = FlightService()
