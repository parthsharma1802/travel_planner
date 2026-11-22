import asyncio
import uuid
from backend.services.journal_storage_service import journal_storage_service
from backend.services.trip_storage_service import trip_storage_service

def test_journal_crud_lifecycle():
    """Test full create -> edit -> save -> reopen/list -> delete lifecycle."""
    test_id = f"test_journal_{uuid.uuid4().hex[:8]}"

    payload = {
        "id": test_id,
        "title": "Golden Sunset at Nahargarh Fort",
        "destination": "Jaipur, Rajasthan",
        "date": "October 16, 2026",
        "content": "We drove up the winding Aravalli hills in the evening. The panoramic view of the Pink City was breathtaking.",
        "photos": ["https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800"],
        "tags": ["Jaipur", "Sunset", "Fort"],
        "author": "Explorer",
        "read_time": "3 min read"
    }

    # 1. CREATE
    created = journal_storage_service.create_post(payload)
    assert created["id"] == test_id
    assert created["title"] == "Golden Sunset at Nahargarh Fort"
    assert created["destination"] == "Jaipur, Rajasthan"
    assert len(created["photos"]) == 1
    print("✓ 1. Create Journal Story passed")

    # 2. REOPEN & GET
    fetched = journal_storage_service.get_post(test_id)
    assert fetched is not None
    assert fetched["destination"] == "Jaipur, Rajasthan"
    assert "Nahargarh" in fetched["title"]
    print("✓ 2. Reopen & Get Journal Story passed")

    # 3. EDIT & SAVE
    updated = journal_storage_service.update_post(test_id, {
        "title": "Magical Sunset at Nahargarh Fort & Jaigarh Ridge",
        "content": "Updated content with cafe notes and photography angles."
    })
    assert updated is not None
    assert updated["title"] == "Magical Sunset at Nahargarh Fort & Jaigarh Ridge"
    assert "photography" in updated["content"]
    re_fetched = journal_storage_service.get_post(test_id)
    assert re_fetched["title"] == "Magical Sunset at Nahargarh Fort & Jaigarh Ridge"
    print("✓ 3. Edit & Save Journal Story passed")

    # 4. LIST POSTS
    all_posts = journal_storage_service.list_posts()
    assert any(p["id"] == test_id for p in all_posts)
    print("✓ 4. List Journal Stories passed")

    # 5. DELETE
    deleted = journal_storage_service.delete_post(test_id)
    assert deleted is True
    assert journal_storage_service.get_post(test_id) is None
    print("✓ 5. Delete Journal Story passed")

def test_convert_trip_to_journal():
    """Test converting a saved trip into a travel journal draft."""
    test_trip_id = f"test_trip_conv_{uuid.uuid4().hex[:8]}"
    trip = {
        "id": test_trip_id,
        "title": "Weekend in Agra & Fatehpur",
        "destination": "Agra",
        "origin": "Delhi",
        "dates": "Nov 2 - Nov 3",
        "duration": "2 Days",
        "hotel": {"hotel_name": "ITC Mughal Agra"},
        "itinerary": {
            "overview": {"title": "Agra Heritage", "destination": "Agra"},
            "days": [
                {
                    "day": 1,
                    "title": "Taj Mahal Sunrise",
                    "morning": "Witness sunrise at Taj Mahal",
                    "afternoon": "Agra Fort exploration",
                    "stay_area": "Taj Ganj"
                }
            ]
        }
    }
    trip_storage_service.create_trip(trip)

    # Convert trip to journal draft
    journal_draft = journal_storage_service.convert_trip_to_journal(test_trip_id)
    assert journal_draft is not None
    assert journal_draft["trip_id"] == test_trip_id
    assert "Agra" in journal_draft["destination"]
    assert "Taj Mahal" in journal_draft["content"]
    print("✓ 6. Convert Saved Trip to Journal Story passed")

    # Cleanup
    journal_storage_service.delete_post(journal_draft["id"])
    trip_storage_service.delete_trip(test_trip_id)

def test_api_journal_routes():
    """Test FastAPI journal endpoints."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 1. GET /api/journal/posts
    res = client.get("/api/journal/posts")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # 2. POST /api/journal/posts
    new_post = {
        "title": "Exploring Spiti Valley by Road",
        "destination": "Spiti Valley, Himachal",
        "content": "A high-altitude desert adventure through Kaza and Key Monastery.",
        "tags": ["Spiti", "Himalayas"]
    }
    create_res = client.post("/api/journal/posts", json=new_post)
    assert create_res.status_code == 200
    post_id = create_res.json()["post"]["id"]

    # 3. GET /api/journal/posts/{id}
    get_res = client.get(f"/api/journal/posts/{post_id}")
    assert get_res.status_code == 200
    assert get_res.json()["post"]["destination"] == "Spiti Valley, Himachal"

    # 4. PUT /api/journal/posts/{id}
    edit_res = client.put(f"/api/journal/posts/{post_id}", json={"title": "Spiti Valley Road Trip Chronicles"})
    assert edit_res.status_code == 200
    assert edit_res.json()["post"]["title"] == "Spiti Valley Road Trip Chronicles"

    # 5. DELETE /api/journal/posts/{id}
    del_res = client.delete(f"/api/journal/posts/{post_id}")
    assert del_res.status_code == 200
    assert client.get(f"/api/journal/posts/{post_id}").status_code == 404
    print("✓ 7. FastAPI Journal API Routes passed")

if __name__ == "__main__":
    test_journal_crud_lifecycle()
    test_convert_trip_to_journal()
    test_api_journal_routes()
    print("\nAll Travel Journal / Blog tests passed successfully!")
