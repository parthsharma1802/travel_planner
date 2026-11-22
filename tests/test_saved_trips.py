import asyncio
import uuid
from backend.services.trip_storage_service import trip_storage_service

def test_trip_storage_crud_lifecycle():
    """Test full create -> save -> reload/list -> open/get -> rename -> delete lifecycle."""
    test_id = f"test_trip_{uuid.uuid4().hex[:8]}"
    
    trip_payload = {
        "id": test_id,
        "title": "5-Day Heritage Tour of Jaipur & Udaipur",
        "destination": "Rajasthan",
        "origin": "New Delhi",
        "dates": "15 Oct - 20 Oct",
        "duration": "5 Days",
        "travelers": "2 Adults",
        "budget": "₹35,000",
        "hotel": {
            "hotel_name": "Rambagh Palace Jaipur",
            "price_inr": 8500,
            "best_vendor": "Booking.com"
        },
        "transport": {
            "mode": "train",
            "name": "Vande Bharat Express #20978",
            "price": 1450
        },
        "itinerary": {
            "overview": {
                "title": "5-Day Heritage Tour of Jaipur & Udaipur",
                "destination": "Rajasthan",
                "origin": "New Delhi",
                "dates": "15 Oct - 20 Oct",
                "duration": "5 Days"
            },
            "days": [
                {
                    "day": 1,
                    "title": "Arrival in Jaipur & Amber Fort",
                    "morning": "Board Vande Bharat from New Delhi to Jaipur",
                    "afternoon": "Check in and visit Amber Fort",
                    "evening": "Stroll through Johari Bazaar and taste Rajasthani cuisine",
                    "stay_area": "Civil Lines, Jaipur"
                },
                {
                    "day": 2,
                    "title": "City Palace & Hawa Mahal",
                    "morning": "Explore City Palace and Jantar Mantar observatory",
                    "afternoon": "Photography at Hawa Mahal",
                    "evening": "Sunset at Nahargarh Fort",
                    "stay_area": "Civil Lines, Jaipur"
                }
            ],
            "summary": {
                "total_distance_km": 650,
                "overnight_stops": 4,
                "highlights": ["Amber Fort", "City Palace", "Nahargarh Fort"]
            }
        },
        "estimated_total": 29800
    }

    # 1. CREATE & SAVE
    created = trip_storage_service.create_trip(trip_payload)
    assert created["id"] == test_id
    assert created["title"] == "5-Day Heritage Tour of Jaipur & Udaipur"
    assert created["destination"] == "Rajasthan"
    assert created["hotel"]["hotel_name"] == "Rambagh Palace Jaipur"
    assert created["transport"]["name"] == "Vande Bharat Express #20978"
    assert len(created["itinerary"]["days"]) == 2
    print("✓ 1. Create & Save Trip passed")

    # 2. RELOAD & LIST
    all_trips = trip_storage_service.list_trips()
    assert any(t["id"] == test_id for t in all_trips)
    print("✓ 2. Reload & List Saved Trips passed")

    # 3. OPEN & GET
    fetched = trip_storage_service.get_trip(test_id)
    assert fetched is not None
    assert fetched["destination"] == "Rajasthan"
    assert fetched["estimated_total"] == 29800
    assert fetched["itinerary"]["overview"]["duration"] == "5 Days"
    print("✓ 3. Open & Restore Saved Trip passed")

    # 4. RENAME
    renamed = trip_storage_service.rename_trip(test_id, "Royal Rajasthan Heritage Expedition")
    assert renamed is not None
    assert renamed["title"] == "Royal Rajasthan Heritage Expedition"
    re_fetched = trip_storage_service.get_trip(test_id)
    assert re_fetched["title"] == "Royal Rajasthan Heritage Expedition"
    print("✓ 4. Rename Saved Trip passed")

    # 5. DELETE
    deleted = trip_storage_service.delete_trip(test_id)
    assert deleted is True
    assert trip_storage_service.get_trip(test_id) is None
    print("✓ 5. Delete Saved Trip passed")

def test_api_saved_trips_endpoints():
    """Test API endpoint behavior with FastAPI TestClient."""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 1. Test GET /api/trips
    res = client.get("/api/trips")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "trips" in data

    # 2. Test POST /api/trips
    test_trip = {
        "title": "Weekend Trip to Agra",
        "destination": "Agra",
        "duration": "2 Days",
        "travelers": "2 Adults",
        "budget": "₹15,000",
        "itinerary": {
            "overview": {"title": "Agra Heritage Weekend", "destination": "Agra"},
            "days": [{"day": 1, "title": "Taj Mahal Visit"}]
        }
    }
    create_res = client.post("/api/trips", json=test_trip)
    assert create_res.status_code == 200
    created_data = create_res.json()
    assert created_data["status"] == "success"
    trip_id = created_data["trip"]["id"]

    # 3. Test GET /api/trips/{trip_id}
    get_res = client.get(f"/api/trips/{trip_id}")
    assert get_res.status_code == 200
    assert get_res.json()["trip"]["destination"] == "Agra"

    # 4. Test PATCH /api/trips/{trip_id}/rename
    rename_res = client.patch(f"/api/trips/{trip_id}/rename", json={"title": "Agra & Fatehpur Sikri Getaway"})
    assert rename_res.status_code == 200
    assert rename_res.json()["trip"]["title"] == "Agra & Fatehpur Sikri Getaway"

    # 5. Test DELETE /api/trips/{trip_id}
    del_res = client.delete(f"/api/trips/{trip_id}")
    assert del_res.status_code == 200

    # 6. Verify 404 after deletion
    get_after_del = client.get(f"/api/trips/{trip_id}")
    assert get_after_del.status_code == 404
    print("✓ 6. FastAPI API Routes for Saved Trips passed")

if __name__ == "__main__":
    test_trip_storage_crud_lifecycle()
    test_api_saved_trips_endpoints()
    print("\nAll Saved Trips & Itineraries tests passed successfully!")
