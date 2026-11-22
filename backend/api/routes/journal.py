import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.journal_storage_service import journal_storage_service

logger = logging.getLogger("smart_travel.api.journal")

router = APIRouter(tags=["Travel Journal"])

class JournalPostRequest(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    destination: Optional[str] = None
    trip_id: Optional[str] = None
    trip_title: Optional[str] = None
    date: Optional[str] = None
    content: Optional[str] = None
    photos: Optional[List[str]] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    read_time: Optional[str] = None

class UpdateJournalPostRequest(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    content: Optional[str] = None
    photos: Optional[List[str]] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    date: Optional[str] = None

@router.get("/journal/posts")
def list_journal_posts():
    """List all private travel journal entries."""
    posts = journal_storage_service.list_posts()
    return {
        "status": "success",
        "total": len(posts),
        "posts": posts
    }

@router.get("/journal/posts/{post_id}")
def get_journal_post(post_id: str):
    """Retrieve a single journal entry by ID."""
    post = journal_storage_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Journal post {post_id} not found")
    return {
        "status": "success",
        "post": post
    }

@router.post("/journal/posts")
def create_journal_post(req: JournalPostRequest):
    """Create a new journal entry."""
    post_dict = req.dict(exclude_unset=True)
    created = journal_storage_service.create_post(post_dict)
    return {
        "status": "success",
        "message": "Journal post created successfully",
        "post": created
    }

@router.put("/journal/posts/{post_id}")
@router.patch("/journal/posts/{post_id}")
def update_journal_post(post_id: str, req: UpdateJournalPostRequest):
    """Update/edit an existing journal entry."""
    updates = req.dict(exclude_unset=True)
    updated = journal_storage_service.update_post(post_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Journal post {post_id} not found")
    return {
        "status": "success",
        "message": "Journal post updated successfully",
        "post": updated
    }

@router.delete("/journal/posts/{post_id}")
def delete_journal_post(post_id: str):
    """Delete a journal entry."""
    deleted = journal_storage_service.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Journal post {post_id} not found")
    return {
        "status": "success",
        "message": f"Journal post {post_id} deleted successfully"
    }

@router.post("/journal/from-trip/{trip_id}")
def convert_trip_to_journal(trip_id: str):
    """Convert a saved itinerary into a new journal entry draft."""
    post = journal_storage_service.convert_trip_to_journal(trip_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Trip {trip_id} not found to convert to journal")
    return {
        "status": "success",
        "message": "Trip converted to journal draft successfully",
        "post": post
    }
