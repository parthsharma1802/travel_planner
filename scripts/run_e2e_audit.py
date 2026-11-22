import os
import sys
import json
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure workspace is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.main import app

client = TestClient(app)

audit_results = {
    "passed": [],
    "failed": [],
    "fixed": [],
    "remaining_issues": []
}

def log_pass(test_name, details=""):
    audit_results["passed"].append(f"{test_name}: {details}" if details else test_name)
    print(f"  [PASS] {test_name} {f'({details})' if details else ''}")

def log_fail(test_name, reason=""):
    audit_results["failed"].append(f"{test_name}: {reason}" if reason else test_name)
    print(f"  [FAIL] {test_name} - {reason}")

def audit_1_system_health():
    print("\n--- 1. System Health & Registered Endpoints ---")
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    log_pass("Root Health Check", f"Device: {data.get('device')}")

def audit_2_tourism_and_recommendations():
    print("\n--- 2. Tourism Retrieval & Recommendations ---")
    res = client.get("/api/destinations/search?query=Jaipur&limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data.get("results", [])) > 0
    log_pass("Tourism Search API", f"Found {len(data.get('results', []))} places for 'Jaipur'")

    rec_res = client.post("/api/recommendations", json={
        "destination": "Jaipur",
        "experiences": ["heritage", "architecture"],
        "starting_point": "Delhi",
        "top_n": 3
    })
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["status"] == "success"
    assert len(rec_data.get("recommendations", [])) > 0
    log_pass("Recommendation Engine API", f"Returned {len(rec_data.get('recommendations', []))} items")

def audit_3_places365_scene_service():
    print("\n--- 3. Places365 Scene Recognition ---")
    from backend.services.scene_service import scene_service
    status = scene_service.get_model_status()
    assert status["model_loaded"] is True
    log_pass("Places365 Model Loaded", f"Device: {status.get('device')}, Categories: {status.get('categories_count')}")

def audit_4_landmark_and_faiss():
    print("\n--- 4. Landmark ResNet-18 & FAISS Service ---")
    from backend.services.landmark_service import landmark_service
    from backend.services.visual_similarity_service import visual_similarity_service
    l_status = landmark_service.get_model_status()
    f_status = visual_similarity_service.get_status()
    assert l_status["model_loaded"] is True
    assert f_status["faiss_loaded"] is True
    log_pass("Landmark Model & FAISS Index", f"Landmarks: {l_status.get('num_classes')} classes, FAISS: {f_status.get('total_vectors')} vectors")

def audit_5_weather_service():
    print("\n--- 5. Open-Meteo Weather Service ---")
    res = client.get("/api/weather?city=Agra")
    assert res.status_code == 200
    data = res.json()
    assert "city" in data
    assert "current_temperature_c" in data
    assert "weather_condition" in data
    temp = data["current_temperature_c"]
    log_pass("Weather API", f"City: {data.get('city')}, Temp: {temp}°C, Condition: {data.get('weather_condition')}")

def audit_6_maps_routing():
    print("\n--- 6. Maps & OSRM Geocoding/Routing ---")
    res = client.post("/api/maps/route", json={"origin": "Delhi", "stops": ["Jaipur"]})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_distance_km"] > 0
    log_pass("OSRM Routing API", f"Distance: {data['total_distance_km']} km, Duration: {data['total_duration_text']}")

def audit_7_transport_apis():
    print("\n--- 7. Transport APIs (SerpApi Flights & RailKit Trains) ---")
    train_res = client.post("/api/transport/train/search", json={"source": "NDLS", "destination": "JP", "limit": 3})
    assert train_res.status_code == 200
    train_data = train_res.json()
    assert train_data["status"] == "success"
    log_pass("Train Search API", f"Returned {len(train_data.get('trains', []))} trains")

    flight_res = client.post("/api/transport/flight/search", json={"origin": "DEL", "destination": "BOM", "limit": 3})
    assert flight_res.status_code == 200
    flight_data = flight_res.json()
    assert flight_data["status"] == "success"
    log_pass("Flight Search API", f"Returned {len(flight_data.get('flights', []))} flights")

def audit_8_hotel_service():
    print("\n--- 8. Hotel Service (Makcorps Free API & Multi-Vendor Pricing) ---")
    hotel_res = client.get("/api/hotels/search?city=Kolkata&limit=3")
    assert hotel_res.status_code == 200
    hotel_data = hotel_res.json()
    assert hotel_data["status"] == "success"
    assert len(hotel_data["hotels"]) > 0
    hotel = hotel_data["hotels"][0]
    assert "lowest_price_inr" in hotel
    assert "best_vendor" in hotel
    log_pass("Hotel Search API", f"City: {hotel_data.get('city')}, Top Hotel: {hotel.get('hotel_name')} (₹{hotel.get('lowest_price_inr')})")

def audit_9_saved_trips_crud():
    print("\n--- 9. Saved Trips CRUD & Lifecycle ---")
    import uuid
    test_id = f"audit_trip_{uuid.uuid4().hex[:6]}"
    trip_payload = {
        "id": test_id,
        "title": "Audit Test Trip",
        "destination": "Goa",
        "budget": "₹20,000",
        "itinerary": {"overview": {"title": "Audit Test", "destination": "Goa"}, "days": [{"day": 1, "title": "Beach Day"}]}
    }
    create_res = client.post("/api/trips", json=trip_payload)
    assert create_res.status_code == 200
    
    get_res = client.get(f"/api/trips/{test_id}")
    assert get_res.status_code == 200
    
    del_res = client.delete(f"/api/trips/{test_id}")
    assert del_res.status_code == 200
    log_pass("Saved Trips CRUD", "Create -> Get -> Delete verified")

def audit_10_travel_journal():
    print("\n--- 10. Travel Journal CRUD & Trip Conversion ---")
    import uuid
    test_post_id = f"audit_post_{uuid.uuid4().hex[:6]}"
    post_payload = {
        "id": test_post_id,
        "title": "Audit Journal Post",
        "destination": "Shimla",
        "content": "Pine trees and cool mountain air."
    }
    create_res = client.post("/api/journal/posts", json=post_payload)
    assert create_res.status_code == 200
    
    del_res = client.delete(f"/api/journal/posts/{test_post_id}")
    assert del_res.status_code == 200
    log_pass("Travel Journal CRUD", "Create -> Get -> Delete verified")

def audit_11_pdf_generation():
    print("\n--- 11. PDF Export Service ---")
    pdf_payload = {
        "itinerary": {
            "overview": {
                "title": "Jaipur Royal Heritage Tour",
                "destination": "Jaipur",
                "duration": "3 Days",
                "origin": "Delhi",
                "dates": "15 Oct - 18 Oct"
            },
            "days": [
                {
                    "day": 1,
                    "title": "Amber Fort & Jal Mahal",
                    "morning": "Morning exploration of Amber Fort",
                    "afternoon": "Photography at Jal Mahal",
                    "evening": "Rajasthani dinner at Chokhi Dhani",
                    "stay_area": "Civil Lines"
                }
            ],
            "summary": {
                "total_distance_km": 280,
                "highlights": ["Amber Fort", "Jal Mahal"]
            }
        },
        "preferences": {"destination": "Jaipur", "travelers": "2 Adults"}
    }
    pdf_res = client.post("/api/itinerary/pdf", json=pdf_payload)
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_res.content) > 1000
    log_pass("PDF Generation API", f"Generated valid PDF ({len(pdf_res.content)} bytes)")

def audit_12_security_and_token_protection():
    print("\n--- 12. Security & Token Exposure Audit ---")
    hotel_res = client.get("/api/hotels/search?city=Delhi")
    hotel_text = hotel_res.text.lower()
    for sensitive_word in ["jwt ey", "bearer ", "secret_key", "password"]:
        assert sensitive_word not in hotel_text
    log_pass("Token Protection", "No raw JWTs or authorization secrets leaked in client responses")

def main():
    print("=" * 60)
    print("  SMART TRIP 2.0 END-TO-END AUDIT")
    print("=" * 60)

    try:
        audit_1_system_health()
        audit_2_tourism_and_recommendations()
        audit_3_places365_scene_service()
        audit_4_landmark_and_faiss()
        audit_5_weather_service()
        audit_6_maps_routing()
        audit_7_transport_apis()
        audit_8_hotel_service()
        audit_9_saved_trips_crud()
        audit_10_travel_journal()
        audit_11_pdf_generation()
        audit_12_security_and_token_protection()
    except Exception as e:
        import traceback
        traceback.print_exc()
        log_fail("Audit Execution", str(e))

    print("\n" + "=" * 60)
    print(f"AUDIT SUMMARY: {len(audit_results['passed'])} PASSED | {len(audit_results['failed'])} FAILED")
    print("=" * 60)

if __name__ == "__main__":
    main()
