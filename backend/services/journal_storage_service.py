import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.services.trip_storage_service import trip_storage_service

logger = logging.getLogger("smart_travel.journal_storage")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
JOURNAL_FILE = DATA_DIR / "journal_posts.json"

class JournalStorageService:
    """
    Persistent storage service for private Travel Journal entries & blog stories.
    """

    def __init__(self):
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if not JOURNAL_FILE.exists():
                with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to initialize journal storage: {e}")

    def _read_posts(self) -> List[Dict[str, Any]]:
        self._ensure_storage_dir()
        try:
            with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to read journal posts: {e}")
            return []

    def _write_posts(self, posts: List[Dict[str, Any]]) -> bool:
        self._ensure_storage_dir()
        try:
            with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to write journal posts: {e}")
            return False

    def list_posts(self) -> List[Dict[str, Any]]:
        """List all personal journal entries, newest first."""
        posts = self._read_posts()
        return sorted(posts, key=lambda p: p.get("updated_at") or p.get("created_at") or "", reverse=True)

    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a journal entry by ID."""
        posts = self._read_posts()
        for p in posts:
            if p.get("id") == post_id:
                return p
        return None

    def create_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new travel journal post."""
        post_id = payload.get("id") or f"journal_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow().isoformat() + "Z"
        
        post = {
            "id": post_id,
            "title": payload.get("title") or "My Travel Journey",
            "destination": payload.get("destination", ""),
            "trip_id": payload.get("trip_id", None),
            "trip_title": payload.get("trip_title", None),
            "date": payload.get("date") or datetime.utcnow().strftime("%B %d, %Y"),
            "content": payload.get("content", ""),
            "photos": payload.get("photos", []),
            "cover_image": payload.get("cover_image") or (payload.get("photos", [None])[0] if payload.get("photos") else None),
            "tags": payload.get("tags", []),
            "author": payload.get("author", "Traveler"),
            "read_time": payload.get("read_time", "3 min read"),
            "created_at": now,
            "updated_at": now
        }

        posts = self._read_posts()
        existing_idx = next((i for i, p in enumerate(posts) if p.get("id") == post_id), None)
        if existing_idx is not None:
            post["created_at"] = posts[existing_idx].get("created_at", now)
            posts[existing_idx] = post
        else:
            posts.insert(0, post)

        self._write_posts(posts)
        return post

    def update_post(self, post_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing journal entry."""
        posts = self._read_posts()
        for idx, post in enumerate(posts):
            if post.get("id") == post_id:
                clean_updates = {k: v for k, v in updates.items() if k not in ["id", "created_at"]}
                post.update(clean_updates)
                post["updated_at"] = datetime.utcnow().isoformat() + "Z"
                posts[idx] = post
                self._write_posts(posts)
                return post
        return None

    def delete_post(self, post_id: str) -> bool:
        """Delete a journal post by ID."""
        posts = self._read_posts()
        initial_len = len(posts)
        filtered = [p for p in posts if p.get("id") != post_id]
        if len(filtered) < initial_len:
            self._write_posts(filtered)
            return True
        return False

    def convert_trip_to_journal(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Convert a saved itinerary/trip into a structured travel journal story draft.
        """
        trip = trip_storage_service.get_trip(trip_id)
        if not trip:
            return None

        dest = trip.get("destination") or "Incredible India"
        title = f"Memories of {trip.get('title') or dest}"
        
        # Build initial story content from itinerary days
        content_sections = [
            f"# {title}\n",
            f"**Destination:** {dest} | **Dates:** {trip.get('dates') or 'Recent Journey'} | **Travelers:** {trip.get('travelers') or 'Family & Friends'}\n",
            "## The Journey Begins\n",
            f"Embarking on our trip from {trip.get('origin') or 'home'} to {dest} was filled with excitement.\n"
        ]

        itinerary = trip.get("itinerary") or {}
        days = itinerary.get("days") or []
        for d in days:
            day_num = d.get("day", 1)
            day_title = d.get("title", f"Day {day_num} Exploration")
            content_sections.append(f"### Day {day_num}: {day_title}")
            if d.get("morning"):
                content_sections.append(f"- **Morning:** {d['morning']}")
            if d.get("afternoon"):
                content_sections.append(f"- **Afternoon:** {d['afternoon']}")
            if d.get("evening"):
                content_sections.append(f"- **Evening:** {d['evening']}")
            if d.get("stay_area"):
                content_sections.append(f"*Stayed around {d['stay_area']}*\n")

        if trip.get("hotel"):
            content_sections.append(f"**Stay Experience:** Loved our stay at {trip['hotel'].get('hotel_name', 'our boutique hotel')}.")

        draft_content = "\n".join(content_sections)

        post_payload = {
            "title": title,
            "destination": dest,
            "trip_id": trip_id,
            "trip_title": trip.get("title"),
            "date": datetime.utcnow().strftime("%B %d, %Y"),
            "content": draft_content,
            "photos": [
                "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80"
            ],
            "tags": [dest, "Travel Story", "Heritage"],
            "author": "Me",
            "read_time": "4 min read"
        }

        return self.create_post(post_payload)


journal_storage_service = JournalStorageService()
