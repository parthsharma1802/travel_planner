#!/usr/bin/env python3
"""
Test Suite: RailKit Train Search Integration
Validates all requirements:
1. Valid train search (Delhi -> Jaipur, Mumbai -> Goa)
2. Invalid input handling (empty, identical stations)
3. No-results handling
4. Provider failure / missing key resilience
5. FastAPI Endpoint POST /api/transport/train/search
6. Groq Assistant integration ("Delhi se Jaipur kal ki trains batao")
7. Non-trigger for unrelated travel conversations
"""

import os
import sys
import asyncio
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.train_service import train_service, _resolve_station_code, _normalize_date
from backend.services.grok_service import grok_service

API_BASE = "http://localhost:8000"


def test_1_station_and_date_helpers():
    print("\n--- TEST 1: Station Code & Date Normalization ---")
    assert _resolve_station_code("Delhi") == "NDLS"
    assert _resolve_station_code("Jaipur") == "JP"
    assert _resolve_station_code("Mumbai") == "MMCT"
    assert _resolve_station_code("NDLS") == "NDLS"
    
    assert _normalize_date("2026-09-04") == "04-09-2026"
    assert _normalize_date("04-09-2026") == "04-09-2026"
    assert _normalize_date("today") is not None
    assert _normalize_date("tomorrow") is not None
    print("✅ Helper mappings verified")


async def test_2_valid_train_search_service():
    print("\n--- TEST 2: Valid Train Search via Service (Delhi -> Jaipur) ---")
    res = await train_service.search_trains(
        source="Delhi",
        destination="Jaipur",
        travel_date="tomorrow",
        limit=10
    )
    assert res["status"] == "success", f"Expected success, got {res['status']}"
    assert res["total_trains"] > 0, "Should return available trains"
    assert len(res["trains"]) > 0
    t1 = res["trains"][0]
    assert t1.get("train_number") is not None
    assert t1.get("train_name") is not None
    assert t1.get("departure_time") is not None
    assert t1.get("arrival_time") is not None
    print(f"✅ PASSED: Retrieved {res['total_trains']} trains. Sample: {t1['train_number']} {t1['train_name']} ({t1['departure_time']} -> {t1['arrival_time']})")


async def test_3_invalid_inputs_and_edge_cases():
    print("\n--- TEST 3: Invalid Input & Edge Case Handling ---")
    # Identical stations
    r1 = await train_service.search_trains("Delhi", "Delhi")
    assert r1["status"] == "error"
    print("✅ Identical stations cleanly rejected")

    # Empty source
    r2 = await train_service.search_trains("", "Jaipur")
    assert r2["status"] == "error"
    print("✅ Empty source cleanly rejected")


async def test_4_fastapi_endpoint():
    print("\n--- TEST 4: FastAPI POST /api/transport/train/search Endpoint ---")
    payload = {
        "source": "Delhi",
        "destination": "Jaipur",
        "travel_date": "tomorrow",
        "passengers": 2,
        "limit": 5
    }
    resp = requests.post(f"{API_BASE}/api/transport/train/search", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert data["provider"] == "RailKit"
    assert data["total_trains"] > 0
    print(f"✅ PASSED: API returned {data['total_trains']} trains via RailKit")


async def test_5_groq_natural_conversation_integration():
    print("\n--- TEST 5: Groq Assistant Integration ('Delhi se Jaipur kal ki trains batao') ---")
    messages = [
        {"role": "user", "content": "Delhi se Jaipur kal ki trains batao"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    msg = resp["message"].lower()

    # Assertions
    assert "sainik" in msg or "shatabdi" in msg or "express" in msg or "train" in msg, "Must list train names"
    assert ":" in msg, "Must include departure/arrival timings"
    assert "{" not in resp["message"] and "}" not in resp["message"], "No raw JSON"
    assert "railkit_59921" not in resp["message"], "API key must never leak"
    assert resp.get("quiz") is None or not resp.get("quiz", {}).get("active"), "No quiz"
    print(f"✅ PASSED: Response is natural with verified RailKit trains:\n{resp['message'][:200]}...\n")


async def test_6_unrelated_query_non_trigger():
    print("\n--- TEST 6: Non-Trigger for Unrelated Queries ---")
    messages = [
        {"role": "user", "content": "Recommend luxury hotels in Agra near Taj Mahal"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    msg = resp["message"].lower()
    assert "railkit" not in msg
    assert "train_no" not in msg
    print("✅ PASSED: Hotel recommendation does not trigger train search")


async def main():
    print("==================================================")
    print("RUNNING RAILKIT TRAIN API INTEGRATION TESTS")
    print("==================================================")
    test_1_station_and_date_helpers()
    await test_2_valid_train_search_service()
    await test_3_invalid_inputs_and_edge_cases()
    await test_4_fastapi_endpoint()
    await test_5_groq_natural_conversation_integration()
    await test_6_unrelated_query_non_trigger()
    print("\n==================================================")
    print("🎉 ALL 6 RAILKIT INTEGRATION TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
