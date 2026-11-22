import os
import sys
import json
import asyncio
import logging
import re
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

logger = logging.getLogger("smart_travel.train_service")
BRIDGE_SCRIPT = os.path.join(ROOT_DIR, "backend", "services", "railkit_bridge.js")

# Canonical Indian City / Hub to Primary Railway Station Code Map
CITY_TO_STATION_CODE: Dict[str, str] = {
    "delhi": "NDLS",
    "new delhi": "NDLS",
    "old delhi": "DLI",
    "delhi cantt": "DEC",
    "delhi sarai rohilla": "DEE",
    "jaipur": "JP",
    "agra": "AGC",
    "agra cantt": "AGC",
    "mumbai": "MMCT",
    "bombay": "MMCT",
    "mumbai central": "MMCT",
    "csmt": "CSMT",
    "goa": "MAO",
    "madgaon": "MAO",
    "vasco": "VSG",
    "varanasi": "BSB",
    "banaras": "BSBS",
    "kolkata": "HWH",
    "calcutta": "HWH",
    "howrah": "HWH",
    "sealdah": "SDAH",
    "chennai": "MAS",
    "madras": "MAS",
    "bangalore": "SBC",
    "bengaluru": "SBC",
    "hyderabad": "HYB",
    "secunderabad": "SC",
    "ahmedabad": "ADI",
    "amritsar": "ASR",
    "lucknow": "LKO",
    "chandigarh": "CDG",
    "bhopal": "BPL",
    "pune": "PUNE",
    "surat": "ST",
    "udaipur": "UDZ",
    "jodhpur": "JU",
    "jaisalmer": "JSM",
    "haridwar": "HW",
    "rishikesh": "YNRK",
    "dehradun": "DDN",
    "patna": "PNBE",
    "puri": "PURI",
    "mysore": "MYS",
    "gwalior": "GWL",
    "kanpur": "CNB",
    "prayagraj": "PRYJ",
    "allahabad": "PRYJ",
    "ayodhya": "AY",
    "mathura": "MTJ",
    "shimla": "SML",
    "jammu": "JAT",
    "katra": "SVDK",
}


def _resolve_station_code(query: str) -> str:
    """Resolve a city name or station code to a standard IRCTC station code."""
    if not query:
        return ""
    q = query.strip()
    if re.match(r"^[A-Z0-9]{2,5}$", q):
        return q.upper()

    q_lower = q.lower()
    if q_lower in CITY_TO_STATION_CODE:
        return CITY_TO_STATION_CODE[q_lower]

    for city, code in CITY_TO_STATION_CODE.items():
        if city in q_lower or q_lower in city:
            return code

    return q.upper()


def _normalize_date(date_str: Optional[str]) -> Optional[str]:
    """Convert various date formats into DD-MM-YYYY required by Indian Railways."""
    if not date_str:
        return None
    d = date_str.strip().lower()

    today = datetime.now()
    if d in ["today", "aaj"]:
        return today.strftime("%d-%m-%Y")
    elif d in ["tomorrow", "kal", "next day"]:
        return (today + timedelta(days=1)).strftime("%d-%m-%Y")
    elif d in ["day after tomorrow", "parson"]:
        return (today + timedelta(days=2)).strftime("%d-%m-%Y")

    if re.match(r"^\d{2}-\d{2}-\d{4}$", d):
        return d

    m_iso = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d)
    if m_iso:
        return f"{m_iso.group(3)}-{m_iso.group(2)}-{m_iso.group(1)}"

    m_slash = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", d)
    if m_slash:
        return f"{int(m_slash.group(1)):02d}-{int(m_slash.group(2)):02d}-{m_slash.group(3)}"

    return None


class TrainService:
    """
    Dual-Provider Train Search Service for SmartTrip.
    Primary: RailKit API/SDK
    Secondary / Fallback: Indian-Rail-Api (erail engine)
    Automatically switches to the fallback provider if the primary fails or is rate-limited.
    """

    def __init__(self):
        self.api_key = os.environ.get("RAILKIT_API_KEY", "")

    def _get_api_key(self) -> str:
        return self.api_key or os.environ.get("RAILKIT_API_KEY", "")

    async def _fetch_railkit(
        self,
        src_code: str,
        dst_code: str,
        norm_date: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Fetch train schedules using RailKit SDK."""
        api_key = self._get_api_key()
        if not api_key:
            return None

        args = ["node", BRIDGE_SCRIPT, "search", src_code, dst_code]
        if norm_date:
            args.append(norm_date)

        try:
            child_env = {**os.environ, "RAILKIT_API_KEY": api_key}
            proc = await asyncio.create_subprocess_exec(
                *args,
                env=child_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            raw_out = stdout.decode("utf-8").strip()
            if not raw_out:
                return None

            payload = json.loads(raw_out)
            if payload.get("success") and payload.get("data"):
                return payload
        except Exception as exc:
            logger.warning(f"RailKit provider lookup exception: {exc}")
        return None

    def _fetch_indian_rail_api_sync(
        self,
        src_code: str,
        dst_code: str,
        norm_date: Optional[str]
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch train schedules using Indian-Rail-Api fallback engine."""
        url = f"https://erail.in/rail/getTrains.aspx?Station_From={src_code}&Station_To={dst_code}&DataSource=0&Language=0&Cache=true"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")

            if not raw or "No direct trains found" in raw or "From station not found" in raw:
                return []

            trains = []
            blocks = raw.split("~~~~~~~~")
            for b in blocks:
                if "~^" in b:
                    parts = b.split("~^")[1].split("~")
                    if len(parts) >= 14:
                        t_num = parts[0].strip()
                        t_name = parts[1].strip()
                        s_name = parts[2].strip()
                        s_code = parts[3].strip()
                        d_name = parts[4].strip()
                        d_code = parts[5].strip()
                        from_name = parts[6].strip() or s_name
                        from_code = parts[7].strip() or s_code
                        to_name = parts[8].strip() or d_name
                        to_code = parts[9].strip() or d_code
                        dep = parts[10].strip().replace(".", ":")
                        arr = parts[11].strip().replace(".", ":")
                        dur_raw = parts[12].strip().replace(".", ":")
                        dur = f"{dur_raw} hrs" if "hrs" not in dur_raw else dur_raw
                        run_days = parts[13].strip()

                        trains.append({
                            "train_no": t_num,
                            "train_name": t_name,
                            "from_stn_name": from_name,
                            "from_stn_code": from_code,
                            "to_stn_name": to_name,
                            "to_stn_code": to_code,
                            "from_time": dep,
                            "to_time": arr,
                            "travel_time": dur,
                            "running_days": run_days,
                            "distance": "300",
                            "halts": 10
                        })
            return trains
        except Exception as err:
            logger.warning(f"Indian-Rail-Api fallback error: {err}")
            return None

    async def search_trains(
        self,
        source: str,
        destination: str,
        travel_date: Optional[str] = None,
        passengers: Optional[int] = 1,
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Search available trains between two stations/cities.
        Tries RailKit first. If unavailable, falls back automatically to Indian-Rail-Api.
        """
        src_code = _resolve_station_code(source)
        dst_code = _resolve_station_code(destination)

        if not src_code or not dst_code:
            return {
                "status": "error",
                "message": "Both source and destination stations are required.",
                "provider": "RailKit / IndianRailApi",
                "source": {"query": source, "station_code": src_code},
                "destination": {"query": destination, "station_code": dst_code},
                "travel_date": travel_date,
                "total_trains": 0,
                "trains": []
            }

        if src_code == dst_code:
            return {
                "status": "error",
                "message": "Source and destination stations cannot be identical.",
                "provider": "RailKit / IndianRailApi",
                "source": {"query": source, "station_code": src_code},
                "destination": {"query": destination, "station_code": dst_code},
                "travel_date": travel_date,
                "total_trains": 0,
                "trains": []
            }

        norm_date = _normalize_date(travel_date)

        # 1. Try Primary: RailKit API
        provider_name = "RailKit"
        raw_trains = []
        railkit_res = await self._fetch_railkit(src_code, dst_code, norm_date)

        if railkit_res and railkit_res.get("data"):
            raw_trains = railkit_res["data"]
            provider_name = "RailKit"
        else:
            # 2. Automatic Fallback: Indian-Rail-Api (erail engine)
            logger.info(f"Primary train provider unavailable or empty. Engaging Indian-Rail-Api fallback for {src_code} -> {dst_code}")
            loop = asyncio.get_event_loop()
            fallback_trains = await loop.run_in_executor(
                None, self._fetch_indian_rail_api_sync, src_code, dst_code, norm_date
            )
            if fallback_trains is not None and len(fallback_trains) > 0:
                raw_trains = fallback_trains
                provider_name = "IndianRailApi (Fallback)"

        if not raw_trains:
            return {
                "status": "no_results",
                "message": f"No direct trains found between {src_code} and {dst_code}.",
                "provider": provider_name,
                "source": {"query": source, "station_code": src_code},
                "destination": {"query": destination, "station_code": dst_code},
                "travel_date": norm_date,
                "total_trains": 0,
                "trains": []
            }

        # Normalize train items
        normalized_trains = []
        for t in raw_trains[:limit]:
            t_num = str(t.get("train_no", "")).strip()
            t_name = str(t.get("train_name", "Express Train")).strip()
            dep = str(t.get("from_time", "")).strip()
            arr = str(t.get("to_time", "")).strip()
            dur = str(t.get("travel_time", "")).strip()
            f_code = str(t.get("from_stn_code", src_code)).strip()
            f_name = str(t.get("from_stn_name", source)).strip()
            t_code = str(t.get("to_stn_code", dst_code)).strip()
            t_name_dst = str(t.get("to_stn_name", destination)).strip()
            dist = str(t.get("distance", "")).strip()
            halts = t.get("halts", 0)
            run_days = str(t.get("running_days", "1111111")).strip()

            normalized_trains.append({
                "train_number": t_num,
                "train_name": t_name,
                "departure_time": dep,
                "arrival_time": arr,
                "duration": dur,
                "from_station_code": f_code,
                "from_station_name": f_name,
                "to_station_code": t_code,
                "to_station_name": t_name_dst,
                "running_days": run_days,
                "distance_km": int(dist) if dist.isdigit() else None,
                "halts": int(halts) if isinstance(halts, int) else 0
            })

        return {
            "status": "success",
            "provider": provider_name,
            "source": {
                "query": source,
                "station_code": src_code,
                "station_name": normalized_trains[0]["from_station_name"] if normalized_trains else source
            },
            "destination": {
                "query": destination,
                "station_code": dst_code,
                "station_name": normalized_trains[0]["to_station_name"] if normalized_trains else destination
            },
            "travel_date": norm_date,
            "passengers": passengers or 1,
            "total_trains": len(normalized_trains),
            "trains": normalized_trains
        }


# Global singleton instance
train_service = TrainService()
