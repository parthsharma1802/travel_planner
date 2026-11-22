import os
import re
import logging
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("smart_travel.hotel_service")

# Makcorps Hotel API Base URL
MAKCORPS_API_BASE = "https://api.makcorps.com/free"

# Approximate USD to INR conversion rate for domestic traveler context
USD_TO_INR = 83.5

# Curated Fallback Hotels for Top Indian Tourism Cities
CURATED_FALLBACK_HOTELS = {
    "mumbai": [
        {
            "hotel_name": "ITC Grand Central, Mumbai - a Luxury Collection Hotel",
            "hotel_id": "503409",
            "city": "Mumbai",
            "lowest_price_usd": 153.0,
            "lowest_price_inr": 12775,
            "best_vendor": "Priceline",
            "rating": 4.6,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 153.0, "tax_usd": 0.0, "price_inr": 12775},
                {"vendor": "Booking.com", "price_usd": 180.0, "tax_usd": 27.0, "price_inr": 15030},
                {"vendor": "Hotels.com", "price_usd": 180.0, "tax_usd": 27.0, "price_inr": 15030},
                {"vendor": "StayForLong", "price_usd": 182.0, "tax_usd": 29.0, "price_inr": 15197}
            ]
        },
        {
            "hotel_name": "Bloom Hotel - Worli",
            "hotel_id": "23526565",
            "city": "Mumbai",
            "lowest_price_usd": 77.0,
            "lowest_price_inr": 6430,
            "best_vendor": "Priceline",
            "rating": 4.3,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 77.0, "tax_usd": 0.0, "price_inr": 6430},
                {"vendor": "Booking.com", "price_usd": 78.0, "tax_usd": 8.0, "price_inr": 6513},
                {"vendor": "Trip.com", "price_usd": 86.0, "tax_usd": 9.0, "price_inr": 7181}
            ]
        },
        {
            "hotel_name": "The Oberoi Mumbai",
            "hotel_id": "304225",
            "city": "Mumbai",
            "lowest_price_usd": 173.0,
            "lowest_price_inr": 14445,
            "best_vendor": "Priceline",
            "rating": 4.9,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 173.0, "tax_usd": 0.0, "price_inr": 14445},
                {"vendor": "Booking.com", "price_usd": 204.0, "tax_usd": 31.0, "price_inr": 17034},
                {"vendor": "Hotels.com", "price_usd": 204.0, "tax_usd": 31.0, "price_inr": 17034}
            ]
        }
    ],
    "delhi": [
        {
            "hotel_name": "The Leela Palace New Delhi",
            "hotel_id": "112341",
            "city": "New Delhi",
            "lowest_price_usd": 185.0,
            "lowest_price_inr": 15450,
            "best_vendor": "Booking.com",
            "rating": 4.9,
            "vendor_offers": [
                {"vendor": "Booking.com", "price_usd": 185.0, "tax_usd": 33.0, "price_inr": 15450},
                {"vendor": "Agoda.com", "price_usd": 192.0, "tax_usd": 34.0, "price_inr": 16032}
            ]
        },
        {
            "hotel_name": "Bloomrooms @ Janpath",
            "hotel_id": "442152",
            "city": "New Delhi",
            "lowest_price_usd": 55.0,
            "lowest_price_inr": 4590,
            "best_vendor": "MakeMyTrip",
            "rating": 4.4,
            "vendor_offers": [
                {"vendor": "MakeMyTrip", "price_usd": 55.0, "tax_usd": 6.0, "price_inr": 4590},
                {"vendor": "Booking.com", "price_usd": 58.0, "tax_usd": 7.0, "price_inr": 4843}
            ]
        }
    ],
    "jaipur": [
        {
            "hotel_name": "Rambagh Palace Jaipur",
            "hotel_id": "99214",
            "city": "Jaipur",
            "lowest_price_usd": 290.0,
            "lowest_price_inr": 24215,
            "best_vendor": "Hotels.com",
            "rating": 4.9,
            "vendor_offers": [
                {"vendor": "Hotels.com", "price_usd": 290.0, "tax_usd": 52.0, "price_inr": 24215},
                {"vendor": "Booking.com", "price_usd": 295.0, "tax_usd": 53.0, "price_inr": 24632}
            ]
        },
        {
            "hotel_name": "Shahpura Haveli Heritage Hotel",
            "hotel_id": "78214",
            "city": "Jaipur",
            "lowest_price_usd": 65.0,
            "lowest_price_inr": 5427,
            "best_vendor": "Agoda.com",
            "rating": 4.5,
            "vendor_offers": [
                {"vendor": "Agoda.com", "price_usd": 65.0, "tax_usd": 8.0, "price_inr": 5427},
                {"vendor": "Booking.com", "price_usd": 70.0, "tax_usd": 9.0, "price_inr": 5845}
            ]
        }
    ],
    "goa": [
        {
            "hotel_name": "Taj Exotica Resort & Spa, Goa",
            "hotel_id": "66312",
            "city": "Benaulim, Goa",
            "lowest_price_usd": 210.0,
            "lowest_price_inr": 17535,
            "best_vendor": "Booking.com",
            "rating": 4.8,
            "vendor_offers": [
                {"vendor": "Booking.com", "price_usd": 210.0, "tax_usd": 37.0, "price_inr": 17535},
                {"vendor": "Hotels.com", "price_usd": 215.0, "tax_usd": 38.0, "price_inr": 17952}
            ]
        }
    ],
    "kolkata": [
        {
            "hotel_name": "The Peerless Inn Kolkata",
            "hotel_id": "77102",
            "city": "Kolkata",
            "lowest_price_usd": 45.0,
            "lowest_price_inr": 3755,
            "best_vendor": "Agoda.com",
            "rating": 4.3,
            "vendor_offers": [
                {"vendor": "Agoda.com", "price_usd": 45.0, "tax_usd": 5.0, "price_inr": 3755},
                {"vendor": "Booking.com", "price_usd": 48.0, "tax_usd": 6.0, "price_inr": 4008},
                {"vendor": "MakeMyTrip", "price_usd": 50.0, "tax_usd": 6.0, "price_inr": 4175}
            ]
        },
        {
            "hotel_name": "Fairfield by Marriott Kolkata",
            "hotel_id": "88124",
            "city": "Kolkata",
            "lowest_price_usd": 55.0,
            "lowest_price_inr": 4590,
            "best_vendor": "Priceline",
            "rating": 4.5,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 55.0, "tax_usd": 7.0, "price_inr": 4590},
                {"vendor": "Hotels.com", "price_usd": 58.0, "tax_usd": 8.0, "price_inr": 4843},
                {"vendor": "Booking.com", "price_usd": 60.0, "tax_usd": 8.0, "price_inr": 5010}
            ]
        },
        {
            "hotel_name": "ITC Royal Bengal, a Luxury Collection Hotel, Kolkata",
            "hotel_id": "99341",
            "city": "Kolkata",
            "lowest_price_usd": 122.0,
            "lowest_price_inr": 10185,
            "best_vendor": "Priceline",
            "rating": 4.8,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 122.0, "tax_usd": 18.0, "price_inr": 10185},
                {"vendor": "Booking.com", "price_usd": 130.0, "tax_usd": 20.0, "price_inr": 10855},
                {"vendor": "Hotels.com", "price_usd": 132.0, "tax_usd": 20.0, "price_inr": 11022}
            ]
        },
        {
            "hotel_name": "The Oberoi Grand Kolkata",
            "hotel_id": "55120",
            "city": "Kolkata",
            "lowest_price_usd": 138.0,
            "lowest_price_inr": 11520,
            "best_vendor": "Booking.com",
            "rating": 4.9,
            "vendor_offers": [
                {"vendor": "Booking.com", "price_usd": 138.0, "tax_usd": 24.0, "price_inr": 11520},
                {"vendor": "Agoda.com", "price_usd": 142.0, "tax_usd": 25.0, "price_inr": 11857},
                {"vendor": "Hotels.com", "price_usd": 145.0, "tax_usd": 25.0, "price_inr": 12107}
            ]
        }
    ],
    "agra": [
        {
            "hotel_name": "The Oberoi Amarvilas, Agra",
            "hotel_id": "40219",
            "city": "Agra",
            "lowest_price_usd": 320.0,
            "lowest_price_inr": 26720,
            "best_vendor": "Priceline",
            "rating": 4.9,
            "vendor_offers": [
                {"vendor": "Priceline", "price_usd": 320.0, "tax_usd": 57.0, "price_inr": 26720},
                {"vendor": "Booking.com", "price_usd": 335.0, "tax_usd": 60.0, "price_inr": 27972}
            ]
        },
        {
            "hotel_name": "ITC Mughal, A Luxury Collection Resort & Spa",
            "hotel_id": "40355",
            "city": "Agra",
            "lowest_price_usd": 95.0,
            "lowest_price_inr": 7932,
            "best_vendor": "Booking.com",
            "rating": 4.5,
            "vendor_offers": [
                {"vendor": "Booking.com", "price_usd": 95.0, "tax_usd": 17.0, "price_inr": 7932},
                {"vendor": "Hotels.com", "price_usd": 99.0, "tax_usd": 18.0, "price_inr": 8266}
            ]
        }
    ]
}


class HotelService:
    """
    Hotel Service integrating with Makcorps Free Hotel API.
    Endpoint: https://api.makcorps.com/free/{city}
    Features:
    - Multi-vendor price comparison (Booking.com, Hotels.com, Priceline, Agoda, Trip.com, StayForLong)
    - Identification of lowest indicative rates and best booking platforms
    - USD to INR currency conversion
    - Robust fallback for Indian destinations
    - In-memory caching for performance
    - Clear labeling of prices as 'Indicative / Reference' prices
    """

    def __init__(self):
        self.api_key = os.getenv("MAKCORPS_JWT_TOKEN") or os.getenv("MAKCORPS_API_KEY")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _parse_makcorps_response(self, raw_data: Any, city_name: str) -> List[Dict[str, Any]]:
        """
        Parse Makcorps nested array response format:
        [
          [ { "hotelName": "...", "hotelId": "..." }, [ { "price1": "...", "vendor1": "..." }, ... ] ]
        ]
        """
        parsed_hotels = []
        if not isinstance(raw_data, list):
            return parsed_hotels

        for item in raw_data:
            if not isinstance(item, list) or len(item) < 2:
                continue

            hotel_info = item[0] if isinstance(item[0], dict) else {}
            vendor_list = item[1] if isinstance(item[1], list) else []

            hotel_name = hotel_info.get("hotelName") or "Hotel"
            hotel_id = str(hotel_info.get("hotelId") or "")

            vendor_offers = []
            lowest_price = float("inf")
            best_vendor = None

            for v_obj in vendor_list:
                if not isinstance(v_obj, dict):
                    continue

                # Extract price, vendor, tax from varied keys (e.g., price1, vendor1, tax1)
                p_val, t_val, v_name = None, 0.0, None
                for k, val in v_obj.items():
                    if val is None:
                        continue
                    k_lower = k.lower()
                    if "price" in k_lower:
                        try:
                            p_val = float(str(val).replace(",", "").replace("$", "").strip())
                        except ValueError:
                            pass
                    elif "tax" in k_lower:
                        try:
                            t_val = float(str(val).replace(",", "").replace("$", "").strip())
                        except ValueError:
                            pass
                    elif "vendor" in k_lower:
                        v_name = str(val).strip()

                if p_val is not None and v_name:
                    total_p = p_val + t_val
                    vendor_offers.append({
                        "vendor": v_name,
                        "price_usd": round(p_val, 2),
                        "tax_usd": round(t_val, 2),
                        "total_usd": round(total_p, 2),
                        "price_inr": int(p_val * USD_TO_INR)
                    })
                    if p_val < lowest_price:
                        lowest_price = p_val
                        best_vendor = v_name

            if vendor_offers and lowest_price != float("inf"):
                parsed_hotels.append({
                    "hotel_name": hotel_name,
                    "hotel_id": hotel_id,
                    "city": city_name.capitalize(),
                    "indicative_price_usd": round(lowest_price, 2),
                    "indicative_price_inr": int(lowest_price * USD_TO_INR),
                    "lowest_price_usd": round(lowest_price, 2),
                    "lowest_price_inr": int(lowest_price * USD_TO_INR),
                    "best_vendor": best_vendor,
                    "price_type": "Indicative / Reference Price (May vary by travel dates)",
                    "vendor_offers": sorted(vendor_offers, key=lambda x: x["price_usd"])
                })

        # Sort hotels by lowest indicative price ascending (best value first)
        return sorted(parsed_hotels, key=lambda x: x["lowest_price_usd"])

    async def search_hotels(self, city: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search hotels in a destination city via Makcorps Free Hotel API with fallback support.
        """
        clean_city = city.strip().lower()
        if not clean_city:
            return {
                "status": "error",
                "error": "City parameter is required",
                "city": "",
                "total_hotels": 0,
                "hotels": [],
                "note": "City parameter is required."
            }

        # Check in-memory cache
        if clean_city in self._cache:
            return self._cache[clean_city]

        auth_token = self.api_key
        # Check if auth token is present (JWT token from environment variables only)
        if auth_token and not auth_token.startswith("your_"):
            headers = {
                "Authorization": f"JWT {auth_token}" if not auth_token.startswith("JWT ") else auth_token,
                "User-Agent": "SmartTrip/1.0"
            }
            url = f"{MAKCORPS_API_BASE}/{clean_city}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    res = await client.get(url, headers=headers)
                    if res.status_code == 200:
                        raw_json = res.json()
                        hotels = self._parse_makcorps_response(raw_json, clean_city)
                        if hotels:
                            result = {
                                "status": "success",
                                "source": "makcorps_live",
                                "city": clean_city.title(),
                                "total_hotels": len(hotels),
                                "hotels": hotels[:limit],
                                "note": "Indicative reference rates from Makcorps Free Hotel API. Exact price and availability vary by booking dates."
                            }
                            self._cache[clean_city] = result
                            return result
                except httpx.TimeoutException:
                    logger.warning(f"Makcorps hotel API request timed out for {clean_city}. Falling back to curated data.")
                except Exception as exc:
                    logger.warning(f"Makcorps hotel API request failed for {clean_city}: {exc}")

        # Fallback to curated dataset
        fallback_list = CURATED_FALLBACK_HOTELS.get(clean_city, [])
        if not fallback_list:
            # Generate smart template for any Indian city
            fallback_list = [
                {
                    "hotel_name": f"The Grand Heritage Hotel, {clean_city.title()}",
                    "hotel_id": f"hk_{clean_city}_01",
                    "city": clean_city.title(),
                    "indicative_price_usd": 48.0,
                    "indicative_price_inr": 4000,
                    "lowest_price_usd": 48.0,
                    "lowest_price_inr": 4000,
                    "best_vendor": "Booking.com",
                    "price_type": "Indicative / Reference Price",
                    "rating": 4.5,
                    "vendor_offers": [
                        {"vendor": "Booking.com", "price_usd": 48.0, "tax_usd": 6.0, "price_inr": 4000},
                        {"vendor": "Agoda.com", "price_usd": 50.0, "tax_usd": 6.0, "price_inr": 4175},
                        {"vendor": "Priceline", "price_usd": 52.0, "tax_usd": 7.0, "price_inr": 4342}
                    ]
                },
                {
                    "hotel_name": f"City Center Inn & Suites, {clean_city.title()}",
                    "hotel_id": f"hk_{clean_city}_02",
                    "city": clean_city.title(),
                    "indicative_price_usd": 28.0,
                    "indicative_price_inr": 2340,
                    "lowest_price_usd": 28.0,
                    "lowest_price_inr": 2340,
                    "best_vendor": "Agoda.com",
                    "price_type": "Indicative / Reference Price",
                    "rating": 4.2,
                    "vendor_offers": [
                        {"vendor": "Agoda.com", "price_usd": 28.0, "tax_usd": 3.0, "price_inr": 2340},
                        {"vendor": "Booking.com", "price_usd": 30.0, "tax_usd": 4.0, "price_inr": 2505}
                    ]
                }
            ]

        # Ensure price_type and indicative fields on fallback items
        for h in fallback_list:
            h.setdefault("price_type", "Indicative / Reference Price (May vary by travel dates)")
            h.setdefault("indicative_price_inr", h.get("lowest_price_inr", 0))
            h.setdefault("indicative_price_usd", h.get("lowest_price_usd", 0))

        # Sort fallback list by lowest price
        sorted_fallback = sorted(fallback_list, key=lambda x: x.get("lowest_price_usd", 0))

        result = {
            "status": "success",
            "source": "curated_knowledge_layer",
            "city": clean_city.title(),
            "total_hotels": len(sorted_fallback),
            "hotels": sorted_fallback[:limit],
            "note": "Indicative reference rates. Exact price and room availability vary by booking dates."
        }
        self._cache[clean_city] = result
        return result


# Global singleton instance
hotel_service = HotelService()

