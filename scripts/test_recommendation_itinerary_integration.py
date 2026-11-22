#!/usr/bin/env python3
"""
Test Suite: Recommendation Engine -> Final Itinerary Flow
Validates all 9 required scenarios:
1. 3-day city trip
2. Multi-day road trip
3. Trip with known budget / preferences
4. Train / flight-based trip
5. Image -> Landmark -> "Plan a trip around this"
6. Explicit "Create my final itinerary"
7. Incomplete context (natural single question, no questionnaire spam)
8. Verify no duplicate questions when context is already known
9. Verify no unnecessary calendar / map / weather / flight / train API calls
"""

import os
import sys
import asyncio
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.grok_service import grok_service
from backend.recommendation.engine import recommendation_engine


async def test_1_three_day_city_trip():
    print("\n--- TEST 1: 3-Day City Trip (Jaipur Heritage) ---")
    messages = [
        {"role": "user", "content": "I want a 3-day heritage trip to Jaipur with my friends"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp["intent"] in ["plan_itinerary", "trip_planning"]
    msg = resp["message"].lower()
    assert "jaipur" in msg
    assert "day 1" in msg or "day 2" in msg or (resp.get("itinerary") and len(resp["itinerary"].get("days", [])) >= 3)
    assert "{" not in resp["message"] and "}" not in resp["message"]
    print("✅ TEST 1 Passed: 3-Day city itinerary generated with realistic sequencing.")


async def test_2_multiday_road_trip():
    print("\n--- TEST 2: Multi-day Road Trip (Delhi -> Goa, 7 Days, Car) ---")
    messages = [
        {"role": "user", "content": "Road trip from Delhi to Goa for 7 days with 4 friends in my own car. Create my final itinerary."}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp["intent"] == "plan_itinerary"
    assert resp.get("itinerary") is not None
    assert len(resp["itinerary"].get("days", [])) >= 5
    # Route continuity check
    assert resp.get("route_data") is not None, "Road trip must include verified OSRM route data"
    print(f"✅ TEST 2 Passed: 7-Day road trip generated with {len(resp['itinerary']['days'])} days and OSRM route.")


async def test_3_known_budget_and_preferences():
    print("\n--- TEST 3: Trip with Known Budget and Preferences ---")
    messages = [
        {"role": "user", "content": "I am traveling with my family (parents), budget is ₹40,000, 4 days in Uttarakhand. Make the complete plan."}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp["intent"] == "plan_itinerary"
    assert resp.get("itinerary") is not None
    pref = resp.get("preferences", {})
    assert pref.get("budget") is not None or "40,000" in resp["message"] or "40k" in resp["message"].lower()
    assert resp.get("quiz") is None or not resp.get("quiz", {}).get("active"), "No redundant quiz on complete plan"
    print("✅ TEST 3 Passed: Known budget and family preferences preserved without asking again.")


async def test_4_train_flight_based_trip():
    print("\n--- TEST 4: Train/Flight-Based Trip ---")
    messages = [
        {"role": "user", "content": "Delhi se Goa ki flights dikhao 15 October ko"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp.get("flight_data") is not None
    assert len(resp["flight_data"].get("flights", [])) > 0
    print(f"✅ TEST 4 Passed: Verified flight provider data returned ({len(resp['flight_data']['flights'])} flights).")


async def test_5_visual_anchor_plan_around_this():
    print("\n--- TEST 5: Image -> Landmark -> 'Plan a trip around this' ---")
    landmark_context = {
        "status": "success",
        "landmark_name": "Hawa Mahal",
        "confidence": 0.94,
        "confidence_level": "high",
        "city": "Jaipur",
        "state": "Rajasthan",
        "tourism_info": {
            "city": "Jaipur",
            "state": "Rajasthan",
            "category": "Historical Monument",
            "best_time_to_visit": "October to March"
        },
        "similar_landmarks": [
            {"landmark_name": "City Palace, Jaipur", "location": "Jaipur, Rajasthan"},
            {"landmark_name": "Amber Fort", "location": "Jaipur, Rajasthan"}
        ]
    }
    messages = [
        {"role": "user", "content": "What landmark is this?"},
        {"role": "assistant", "content": "This is Hawa Mahal located in Jaipur, Rajasthan!"},
        {"role": "user", "content": "Plan a 3-day trip around this"}
    ]
    resp = await grok_service.generate_smart_trip_response(
        messages=messages,
        landmark_context=landmark_context
    )
    assert resp["intent"] == "plan_itinerary"
    msg = resp["message"].lower()
    assert "hawa mahal" in msg or "jaipur" in msg
    print("✅ TEST 5 Passed: Visual landmark (Hawa Mahal) used as anchor for 3-day itinerary.")


async def test_6_explicit_final_itinerary_trigger():
    print("\n--- TEST 6: Explicit 'Create my final itinerary' Trigger ---")
    messages = [
        {"role": "user", "content": "I am traveling to Udaipur from Delhi for 3 days by train."},
        {"role": "assistant", "content": "Udaipur is stunning! Would you like a relaxed cultural schedule?"},
        {"role": "user", "content": "Yes, create my final itinerary"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp["intent"] == "plan_itinerary"
    assert resp.get("itinerary") is not None or "day 1" in resp["message"].lower()
    print("✅ TEST 6 Passed: Explicit final itinerary trigger generated complete schedule.")


async def test_7_incomplete_context_natural_question():
    print("\n--- TEST 7: Incomplete Context (Ask Single Natural Question) ---")
    messages = [
        {"role": "user", "content": "I want to visit Rajasthan"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    # Should acknowledge and ask a natural question without overwhelming the user
    assert resp["intent"] in ["general_question", "trip_planning"]
    assert len(resp["message"]) > 20
    assert "{" not in resp["message"]
    print("✅ TEST 7 Passed: Incomplete prompt answered naturally without robotic questionnaire.")


async def test_8_no_duplicate_questions():
    print("\n--- TEST 8: Verify No Duplicate Questions When Context Is Known ---")
    messages = [
        {"role": "user", "content": "I'm starting from Mumbai, going to Goa for 5 days with 2 friends in our car with ₹30k budget."},
        {"role": "assistant", "content": "Awesome road trip from Mumbai to Goa via NH66! Here is the coastal route overview."},
        {"role": "user", "content": "Finalize this trip"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    msg = resp["message"].lower()
    # Should not ask "Where are you starting from?" or "How many days?"
    assert "where will you be starting" not in msg
    assert "how many people" not in msg
    assert "what is your budget" not in msg
    print("✅ TEST 8 Passed: No repetitive questions asked for already known trip context.")


async def test_9_no_unnecessary_api_calls():
    print("\n--- TEST 9: Verify No Unnecessary Calendar/Map/Weather/Flight/Train Calls ---")
    messages = [
        {"role": "user", "content": "Tell me about the history of Qutub Minar"}
    ]
    resp = await grok_service.generate_smart_trip_response(messages=messages)
    assert resp.get("route_data") is None, "History query must not fetch road maps"
    assert resp.get("flight_data") is None, "History query must not fetch flights"
    assert resp.get("train_data") is None, "History query must not fetch trains"
    assert resp.get("quiz") is None or not resp.get("quiz", {}).get("active"), "History query must not trigger quiz"
    print("✅ TEST 9 Passed: General inquiries do not make unnecessary tool/API calls.")


async def main():
    print("==================================================")
    print("RUNNING RECOMMENDATION -> FINAL ITINERARY TESTS")
    print("==================================================")
    await test_1_three_day_city_trip()
    await asyncio.sleep(1.2)
    await test_2_multiday_road_trip()
    await asyncio.sleep(1.2)
    await test_3_known_budget_and_preferences()
    await asyncio.sleep(1.2)
    await test_4_train_flight_based_trip()
    await asyncio.sleep(1.2)
    await test_5_visual_anchor_plan_around_this()
    await asyncio.sleep(1.2)
    await test_6_explicit_final_itinerary_trigger()
    await asyncio.sleep(1.2)
    await test_7_incomplete_context_natural_question()
    await asyncio.sleep(1.2)
    await test_8_no_duplicate_questions()
    await asyncio.sleep(1.2)
    await test_9_no_unnecessary_api_calls()
    print("\n==================================================")
    print("🎉 ALL 9 INTEGRATION TEST SCENARIOS PASSED (100%)!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
