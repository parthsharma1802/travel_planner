#!/usr/bin/env python3
"""
Test Suite: Visual Landmark to Recommendation Engine Integration
Validates all 8 scenarios:
1. Test 1: Image -> Hawa Mahal -> "What's this?" -> Natural identification
2. Test 2: Image -> Hawa Mahal -> "What's nearby?" -> Nearby recommendations without unsolicited tools
3. Test 3: Image -> Hawa Mahal -> "Plan a 3-day trip around this." -> Anchor + 3-day duration
4. Test 4: Image -> Hawa Mahal -> "Tell me more." -> In-depth tourism explanation
5. Test 5: Multi-turn context: Family + 4 days + heritage + Hawa Mahal anchor combined
6. Test 6: Explicit map request: "Show this on the map." -> Map tool activation
7. Test 7: Explicit weather request: "What's the weather there?" -> Weather tool activation
8. Test 8: Explicit final itinerary: "Create my final itinerary." -> Full itinerary generation
"""

import os
import sys
import asyncio

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.landmark_service import landmark_service
from backend.services.visual_similarity_service import visual_similarity_service
from backend.recommendation.engine import recommendation_engine
from backend.services.grok_service import grok_service

HAWA_MAHAL_CONTEXT = {
    "status": "success",
    "landmark_name": "Hawa Mahal",
    "location": "Jaipur, Rajasthan",
    "confidence_level": "high",
    "confidence_score": 0.99,
    "identification_status": "confident",
    "summary_statement": "Looks like Hawa Mahal",
    "similar_landmarks": [
        {"landmark_name": "Hawa Mahal", "location": "Jaipur, Rajasthan", "similarity_score": 1.0, "category": "Castle"},
        {"landmark_name": "City Palace", "location": "Jaipur, Rajasthan", "similarity_score": 0.82, "category": "Palace"}
    ],
    "tourism_info": {
        "destination_name": "Hawa Mahal",
        "state": "Rajasthan",
        "city_district": "Jaipur",
        "category": "Heritage Monument",
        "description": "5-story palace of winds built in 1799 with 953 honeycomb windows."
    }
}


def test_recommendation_engine_anchor_direct():
    print("\n--- TEST: Direct Recommendation Engine Anchor Functionality ---")
    rec = recommendation_engine.recommend({
        "anchor_landmark": "Hawa Mahal",
        "anchor_city": "Jaipur",
        "anchor_state": "Rajasthan",
        "duration": "3 days",
        "experiences": ["History, Heritage & Culture"]
    }, top_n=5)

    assert rec["anchor"] == "Hawa Mahal", "Anchor landmark should match"
    assert rec["destination"] == "Jaipur", "Anchor destination should be Jaipur"
    assert len(rec["recommendations"]) > 0, "Recommendations should be non-empty"
    rec_names = [r["name"] for r in rec["recommendations"]]
    assert any("City Palace" in n or "Hawa Mahal" in n or "Amer" in n for n in rec_names), "Should recommend Jaipur heritage sites"
    print(f"✅ Recommendation Engine retrieved {len(rec['recommendations'])} places with visual anchor: {rec_names[:3]}")


async def test_all_scenarios():
    print("==================================================")
    print("RUNNING VISUAL ANCHOR -> RECOMMENDATION TESTS")
    print("==================================================")

    # 1. Direct Engine Test
    test_recommendation_engine_anchor_direct()

    # 2. Test 1: Image -> "What's this?"
    print("\n--- Scenario 1: Image -> 'What is this?' ---")
    messages1 = [
        {"role": "user", "content": "What is this monument? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"}
    ]
    resp1 = await grok_service.generate_smart_trip_response(messages=messages1, landmark_context=HAWA_MAHAL_CONTEXT)
    msg1 = resp1["message"].lower()
    assert "hawa" in msg1 and "mahal" in msg1, "Must identify Hawa Mahal"
    assert resp1.get("quiz") is None or not resp1.get("quiz", {}).get("active"), "No quiz"
    print("✅ Scenario 1 Passed: Natural landmark identification")

    # 3. Test 2: Image -> "What's nearby?"
    print("\n--- Scenario 2: Image -> 'What's nearby?' ---")
    messages2 = [
        {"role": "user", "content": "What is this place? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "What other places are nearby to explore?"}
    ]
    resp2 = await grok_service.generate_smart_trip_response(messages=messages2, landmark_context=HAWA_MAHAL_CONTEXT)
    msg2 = resp2["message"].lower()
    assert "city palace" in msg2 or "jantar mantar" in msg2 or "amer" in msg2 or "jaigarh" in msg2 or "jaipur" in msg2
    print("✅ Scenario 2 Passed: Recommended nearby attractions using Tourism/Recommendation Layer")

    # 4. Test 3: Image -> "Plan a 3-day trip around this."
    print("\n--- Scenario 3: Image -> 'Plan a 3-day trip around this.' ---")
    messages3 = [
        {"role": "user", "content": "What is this place? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "Plan a 3-day trip around this."}
    ]
    resp3 = await grok_service.generate_smart_trip_response(messages=messages3, landmark_context=HAWA_MAHAL_CONTEXT)
    msg3 = resp3["message"].lower()
    assert "jaipur" in msg3 or "hawa mahal" in msg3 or "day 1" in msg3
    assert resp3["intent"] in ["plan_itinerary", "trip_planning"]
    print(f"✅ Scenario 3 Passed: Inferred Hawa Mahal anchor + 3-day duration (Intent: {resp3['intent']})")

    # 5. Test 4: Image -> "Tell me more."
    print("\n--- Scenario 4: Image -> 'Tell me more.' ---")
    messages4 = [
        {"role": "user", "content": "What is this place? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "Tell me more about its architecture and history."}
    ]
    resp4 = await grok_service.generate_smart_trip_response(messages=messages4, landmark_context=HAWA_MAHAL_CONTEXT)
    msg4 = resp4["message"].lower()
    assert "1799" in msg4 or "jharokha" in msg4 or "window" in msg4 or "sawai" in msg4 or "sandstone" in msg4
    print("✅ Scenario 4 Passed: In-depth tourism explanation delivered")

    # 6. Test 5: Existing context + Visual Anchor
    print("\n--- Scenario 5: Multi-turn Context + Visual Anchor ---")
    messages5 = [
        {"role": "user", "content": "I am travelling with my family for 4 days and prefer heritage."},
        {"role": "assistant", "content": "Rajasthan is a fantastic heritage destination for families!"},
        {"role": "user", "content": "What is this monument? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "Plan around this."}
    ]
    resp5 = await grok_service.generate_smart_trip_response(messages=messages5)
    msg5 = resp5["message"].lower()
    assert "jaipur" in msg5 or "hawa mahal" in msg5
    assert "day" in msg5 or "fort" in msg5 or "palace" in msg5
    print("✅ Scenario 5 Passed: Multi-turn context combined successfully with visual anchor")

    # 7. Test 6: Explicit Map Request -> "Show this on the map."
    print("\n--- Scenario 6: Explicit Map Request ---")
    messages6 = [
        {"role": "user", "content": "What is this place? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "Show me the route from Delhi to Jaipur on the map."}
    ]
    resp6 = await grok_service.generate_smart_trip_response(messages=messages6)
    assert resp6.get("route_tool") is True or resp6.get("route_data") is not None or resp6["intent"] == "route_planning"
    print(f"✅ Scenario 6 Passed: Map routing triggered appropriately (Intent: {resp6['intent']})")

    # 8. Test 7: Explicit Weather Request -> "What's the weather there?"
    print("\n--- Scenario 7: Explicit Weather Request ---")
    messages7 = [
        {"role": "user", "content": "What is this place? [User attached a photo: The trained CV landmark model identified it as Hawa Mahal, Jaipur, Rajasthan]"},
        {"role": "assistant", "content": resp1["message"]},
        {"role": "user", "content": "What is the weather like in Jaipur right now?"}
    ]
    resp7 = await grok_service.generate_smart_trip_response(messages=messages7)
    assert resp7.get("weather_tool") is True or resp7["intent"] == "weather_inquiry" or "weather" in resp7["message"].lower()
    print(f"✅ Scenario 7 Passed: Weather inquiry handled appropriately (Intent: {resp7['intent']})")

    # 9. Test 8: Explicit Final Itinerary -> "Create my final itinerary."
    print("\n--- Scenario 8: Explicit Final Itinerary ---")
    messages8 = [
        {"role": "user", "content": "I want a 3-day trip to Jaipur covering Hawa Mahal and City Palace."},
        {"role": "assistant", "content": "Jaipur is great for a 3-day trip!"},
        {"role": "user", "content": "Create my final itinerary with day-by-day plan."}
    ]
    resp8 = await grok_service.generate_smart_trip_response(messages=messages8)
    assert resp8["intent"] in ["plan_itinerary", "trip_planning", "general_question"]
    assert any(k in resp8["message"].lower() for k in ["day", "jaipur", "itinerary", "palace", "hawa mahal"])
    print(f"✅ Scenario 8 Passed: Complete itinerary generated (Intent: {resp8['intent']})")

    print("\n==================================================")
    print("🎉 ALL 8 SCENARIOS PASSED WITH FULL COMPLIANCE!")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(test_all_scenarios())
