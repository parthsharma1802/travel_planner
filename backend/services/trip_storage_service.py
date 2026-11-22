import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("smart_travel.trip_storage")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STORAGE_FILE = DATA_DIR / "saved_trips.json"

class TripStorageService:
    """
    Persistent storage service for saved trips and itineraries.
    Stores clean, structured trip data with no sensitive tokens or payment data.
    """

    def __init__(self):
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if not STORAGE_FILE.exists():
                with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to initialize trip storage directory: {e}")

    def _read_trips(self) -> List[Dict[str, Any]]:
        self._ensure_storage_dir()
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to read saved trips from file: {e}")
            return []

    def _write_trips(self, trips: List[Dict[str, Any]]) -> bool:
        self._ensure_storage_dir()
        try:
            with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(trips, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to write saved trips to file: {e}")
            return False

    def _sanitize_trip_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Strip any sensitive keys or internal API credentials."""
        clean = {}
        for k, v in data.items():
            k_lower = k.lower()
            if any(s in k_lower for s in ["token", "key", "secret", "password", "jwt", "card", "cvv", "auth"]):
                continue
            clean[k] = v
        return clean

    def list_trips(self) -> List[Dict[str, Any]]:
        """Return all saved trips sorted by updated_at descending."""
        trips = self._read_trips()
        return sorted(trips, key=lambda t: t.get("updated_at") or t.get("created_at") or "", reverse=True)

    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific trip by its unique ID."""
        trips = self._read_trips()
        for trip in trips:
            if trip.get("id") == trip_id:
                return trip
        return None

    def create_trip(self, trip_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create and persist a new trip itinerary."""
        sanitized = self._sanitize_trip_payload(trip_payload)
        trip_id = sanitized.get("id") or f"trip_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow().isoformat() + "Z"

        dest = sanitized.get("destination") or "Custom Destination"
        duration = sanitized.get("duration") or sanitized.get("duration_days") or "3 Days"
        default_title = f"{duration} Trip to {dest}" if dest else "Smart Trip Itinerary"

        trip = {
            "id": trip_id,
            "title": sanitized.get("title") or default_title,
            "destination": sanitized.get("destination", ""),
            "origin": sanitized.get("origin", ""),
            "dates": sanitized.get("dates", ""),
            "duration": str(duration),
            "travelers": sanitized.get("travelers", "2 Travelers"),
            "budget": sanitized.get("budget", ""),
            "transport": sanitized.get("transport", None),
            "hotel": sanitized.get("hotel", None),
            "itinerary": sanitized.get("itinerary", None),
            "route_data": sanitized.get("route_data", None),
            "estimated_total": sanitized.get("estimated_total", 0),
            "notes": sanitized.get("notes", ""),
            "created_at": now,
            "updated_at": now
        }

        trips = self._read_trips()
        # If trip already exists with this ID, update it
        existing_idx = next((i for i, t in enumerate(trips) if t.get("id") == trip_id), None)
        if existing_idx is not None:
            trip["created_at"] = trips[existing_idx].get("created_at", now)
            trips[existing_idx] = trip
        else:
            trips.insert(0, trip)

        self._write_trips(trips)
        return trip

    def update_trip(self, trip_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update fields of an existing saved trip."""
        trips = self._read_trips()
        for idx, trip in enumerate(trips):
            if trip.get("id") == trip_id:
                sanitized_updates = self._sanitize_trip_payload(updates)
                # Don't overwrite the ID or created_at
                sanitized_updates.pop("id", None)
                sanitized_updates.pop("created_at", None)
                trip.update(sanitized_updates)
                trip["updated_at"] = datetime.utcnow().isoformat() + "Z"
                trips[idx] = trip
                self._write_trips(trips)
                return trip
        return None

    def rename_trip(self, trip_id: str, new_title: str) -> Optional[Dict[str, Any]]:
        """Rename a saved trip."""
        if not new_title or not new_title.strip():
            return None
        return self.update_trip(trip_id, {"title": new_title.strip()})

    def delete_trip(self, trip_id: str) -> bool:
        """Delete a saved trip by ID."""
        trips = self._read_trips()
        initial_len = len(trips)
        filtered_trips = [t for t in trips if t.get("id") != trip_id]
        if len(filtered_trips) < initial_len:
            self._write_trips(filtered_trips)
            return True
        return False


trip_storage_service = TripStorageService()
