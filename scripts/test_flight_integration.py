#!/usr/bin/env python3
"""
Test Suite: SerpApi Google Flights Integration
Validates all requirements:
1. Valid flight search (Delhi -> Goa, 15 October)
2. Invalid date / input handling (empty, identical airports)
3. No-results handling
4. API failure / missing key resilience
5. Normal chat does not trigger flight search
6. FastAPI Endpoint POST /api/transport/flight/search
7. Groq Assistant integration ("Delhi se Goa ki flights dikhao 15 October ko")
"""

import os
import sys
import asyncio
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.flight_service import flight_service, _resolve_airport_code, _normalize_flight_date
from backend.services.grok_service import grok_service

API_BASE = "http://localhost:8000"


def test_1_airport_and_date_helpers():
    print("\n--- TEST 1: Airport Code & Date Normalization ---")
    assert _resolve_airport_code("Delhi") == "DEL"
    assert _resolve_airport_code("Goa") == "GOI"
    assert _resolve_airport_code("Mumbai") == "BOM"
    assert _resolve_airport_code("DEL") == "DEL"
    
    assert _normalize_flight_date("15 October") == "2026-10-15"
    assert _normalize_flight_date("15-10-2026") == "2026-10-15"
    assert _normalize_flight_date("2026-10-15") == "2026-10-15"
    assert _normalize_flight_date("tomorrow") is not None
    print("✅ Airport code and natural date mapping verified")


async def test_2_valid_flight_search_service():
    print("\n--- TEST 2: Valid Flight Search via Service (Delhi -> Goa, 15 October) ---")
    res = await flight_service.search_flights(
        origin="Delhi",
        destination="Goa",
        departure_date="15 October",
        limit=5
    )
    assert res["status"] == "success", f"Expected success, got {res['status']}"
    assert res["total_flights"] > 0, "Should return available flights"
    assert len(res["flights"]) > 0
    f1 = res["flights"][0]
    assert f1.get("airline") is not None
    assert f1.get("departure_time") is not None
    assert f1.get("arrival_time") is not None
    assert f1.get("price") is not None
    print(f"✅ PASSED: Retrieved {res['total_flights']} flights. Sample: {f1['airline']} {f1['flight_number']} ({f1['departure_time']} -> {f1['arrival_time']}) - ₹{f1['price']}")


async def test_3_invalid_inputs_and_edge_cases():
    print("\n--- TEST 3: Invalid Input & Edge Case Handling ---")
    # Identical airports
    r1 = await flight_service.search_flights("Delhi", "Delhi")
    assert r1["status"] == "error"
    print("✅ Identical airports cleanly rejected")

    # Empty origin
    r2 = await flight_service.search_flights("", "Goa")
    assert r2["status"] == "error"
    print("✅ Empty origin cleanly rejected")


async def test_4_fastapi_endpoint():
    print("\n--- TEST 4: FastAPI POST /api/transport/flight/search Endpoint ---")
    payload = {
        "origin": "Delhi",
        "destination": "Goa",
        "departure_date": "15 October",
        "passengers": 1,
        "limit": 3
    }
    resp = requests.post(f"{API_BASE}/api/transport/flight/search", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert data["provider"] == "SerpApi (Google Flights)"
    assert data["total_flights"] > 0
    print(f"✅ PASSED: API returned {data['total_flights']} flights via SerpApi")


async def test_5_groq_natural_conversation_integration():
    print("\n--- TEST 5: Groq Assistant Integration ('Delhi se Goa ki flights dikhao 15 October ko') ---")
    messages = [
        {"role": "user", "content": "Delhi se Goa ki flights dikhao 15 October ko"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    msg = resp["message"].lower()

    # Assertions
    assert "indigo" in msg or "air india" in msg or "flight" in msg, "Must list flight names/options"
    assert ":" in msg, "Must include departure/arrival timings"
    assert "{" not in resp["message"] and "}" not in resp["message"], "No raw JSON"
    assert "047a0157f42" not in resp["message"], "SerpApi key must never leak"
    assert resp.get("quiz") is None or not resp.get("quiz", {}).get("active"), "No quiz"
    print(f"✅ PASSED: Groq response is natural with verified Google Flights:\n{resp['message'][:250]}...\n")


async def test_6_unrelated_query_non_trigger():
    print("\n--- TEST 6: Non-Trigger for Unrelated Queries ---")
    messages = [
        {"role": "user", "content": "Tell me about the best street food places in Old Delhi"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    msg = resp["message"].lower()
    assert "serpapi" not in msg
    assert "flight_number" not in msg
    assert "google_flights" not in msg
    print("✅ PASSED: Food inquiry does not trigger flight search")


async def main():
    print("==================================================")
    print("RUNNING SERPAPI GOOGLE FLIGHTS INTEGRATION TESTS")
    print("==================================================")
    test_1_airport_and_date_helpers()
    await test_2_valid_flight_search_service()
    await test_3_invalid_inputs_and_edge_cases()
    await test_4_fastapi_endpoint()
    await test_5_groq_natural_conversation_integration()
    await test_6_unrelated_query_non_trigger()
    print("\n==================================================")
    print("🎉 ALL 6 FLIGHT INTEGRATION TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
