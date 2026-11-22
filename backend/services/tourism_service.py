import os
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger("smart_travel.tourism_service")

DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../data/processed/tourism_master.csv")

class DestinationRecord(BaseModel):
    destination_id: str
    destination_name: str
    state: str
    city_district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = "Tourist Attraction"
    rating: Optional[float] = None
    reviews_count: Optional[float] = None
    price_info: Optional[str] = None
    ideal_seasonality: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    source_dataset: Optional[str] = None

class TourismService:
    """
    Tourism Knowledge Layer Service.
    Loads data/processed/tourism_master.csv in-memory once on initialization.
    Provides fast indexed filtering and keyword search for destinations across India.
    """

    def __init__(self, csv_path: str = DATASET_PATH):
        self.csv_path = os.path.abspath(csv_path)
        self._df: Optional[pd.DataFrame] = None
        self._records: List[Dict[str, Any]] = []
        self._load_dataset()

    def _load_dataset(self):
        """Load and normalize dataset in memory safely handling missing/NaN values."""
        if not os.path.exists(self.csv_path):
            logger.error(f"Dataset path not found: {self.csv_path}")
            return

        try:
            df = pd.read_csv(self.csv_path)
            
            # Fill NaN values safely
            df = df.where(pd.notnull(df), None)
            
            # Normalize numeric types
            if "rating" in df.columns:
                df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
            if "reviews_count" in df.columns:
                df["reviews_count"] = pd.to_numeric(df["reviews_count"], errors="coerce")

            self._df = df
            raw_records = df.to_dict(orient="records")
            
            # Clean records into normalized Python dicts
            self._records = []
            for item in raw_records:
                clean_item = {
                    "destination_id": str(item.get("destination_id") or "UNKNOWN"),
                    "destination_name": str(item.get("destination_name") or ""),
                    "state": str(item.get("state") or "India"),
                    "city_district": str(item.get("city_district")) if item.get("city_district") else None,
                    "latitude": float(item["latitude"]) if item.get("latitude") and not pd.isna(item["latitude"]) else None,
                    "longitude": float(item["longitude"]) if item.get("longitude") and not pd.isna(item["longitude"]) else None,
                    "category": str(item.get("category")) if item.get("category") else "Tourist Attraction",
                    "rating": float(item["rating"]) if item.get("rating") and not pd.isna(item["rating"]) else None,
                    "reviews_count": float(item["reviews_count"]) if item.get("reviews_count") and not pd.isna(item["reviews_count"]) else None,
                    "price_info": str(item.get("price_info")) if item.get("price_info") else None,
                    "ideal_seasonality": str(item.get("ideal_seasonality")) if item.get("ideal_seasonality") else None,
                    "description": str(item.get("description")) if item.get("description") else None,
                    "website_url": str(item.get("website_url")) if item.get("website_url") else None,
                    "source_dataset": str(item.get("source_dataset")) if item.get("source_dataset") else None,
                }
                self._records.append(clean_item)

            logger.info(f"Successfully loaded {len(self._records)} tourism master records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading tourism master dataset: {e}")
            self._records = []

    def search_destinations(
        self,
        query: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search & filter destinations by text query, state, category, and minimum rating.

        Args:
            query: Free text query (e.g., 'historical', 'fort', 'beach')
            state: Filter by state name (e.g., 'Rajasthan', 'Goa')
            category: Filter by category (e.g., 'Tourist Attraction')
            min_rating: Filter by minimum rating (e.g., 4.0)
            limit: Maximum number of records to return

        Returns:
            List of structured DestinationRecord dictionaries
        """
        results = []
        
        q_clean = query.strip().lower() if query else ""
        s_clean = state.strip().lower() if state else ""
        c_clean = category.strip().lower() if category else ""

        for item in self._records:
            item_state = (item["state"] or "").lower()
            item_name = (item["destination_name"] or "").lower()
            item_district = (item["city_district"] or "").lower()
            item_category = (item["category"] or "").lower()
            item_desc = (item["description"] or "").lower()

            # State / City District Filter
            if s_clean and (s_clean not in item_state and s_clean not in item_district and s_clean not in item_name):
                continue

            # Category Filter
            if c_clean and c_clean not in item_category:
                continue

            # Rating Filter
            if min_rating is not None:
                rating = item.get("rating")
                if rating is None or rating < min_rating:
                    continue

            # Keyword Match Score calculation
            score = 0
            if q_clean:
                if q_clean in item_name:
                    score += 10
                if q_clean in item_state:
                    score += 5
                if q_clean in item_district:
                    score += 5
                if q_clean in item_category:
                    score += 3
                if q_clean in item_desc:
                    score += 2

                # If query specified but zero keyword match, skip
                if score == 0:
                    continue

            results.append((score, item.get("rating") or 0.0, item))

        # Sort by relevance score desc, rating desc
        results.sort(key=lambda x: (x[0], x[1]), reverse=True)

        return [r[2] for r in results[:limit]]

    def get_destination_by_id(self, dest_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single destination by exact destination_id."""
        for item in self._records:
            if item["destination_id"] == dest_id:
                return item
        return None

# Global singleton tourism service instance
tourism_service = TourismService()
