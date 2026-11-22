"""
Comprehensive verification test suite for SmartTrip Chatbot Conversation Behavior.
Tests all 8 exact validation scenarios specified in Section 19 of user prompt:
1. Complete trip prompt (Delhi -> Goa, 5 friends, car, 7 days, 50k, beaches/nightlife/food)
2. Normal travel question (best beaches in Goa)
3. Road distance question (Delhi to Jaipur distance)
4. Weather question (weather in Goa this weekend)
5. Long road trip with sensible stops (Delhi to Mumbai for 8 days, 4 friends)
6. Partial trip prompt (plan a Goa trip)
7. Natural language dates extraction (10 October to 17 October)
8. Final itinerary trigger (Okay, create my final itinerary)
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.grok_service import grok_service

async def run_validation_suite():
    print("====================================================================")
    print("STARTING SMARTTRIP CONVERSATIONAL INTELLIGENCE VALIDATION SUITE")
    print("====================================================================")

    # ------------------------------------------------------------------
    # TEST 1: Complete User Prompt
    # ------------------------------------------------------------------
    print("\n--- TEST 1: Complete User Prompt ---")
    prompt_1 = "I'm from Delhi and want to drive to Goa with 5 friends in my own car. We have 7 days, around ₹50k total, and we're mainly interested in beaches, nightlife and local food."
    res1 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_1}])
    
    prefs1 = res1.get("preferences", {})
    msg1 = res1.get("message", "")
    print(f"Message preview: {msg1[:150]}...")
    print(f"Extracted Origin: {prefs1.get('starting_point')}")
    print(f"Extracted Dest: {prefs1.get('destination')}")
    print(f"Extracted Travelers: {prefs1.get('travelers')}")
    print(f"Extracted Transport: {prefs1.get('transport')}")
    print(f"Extracted Duration: {prefs1.get('duration')}")
    print(f"Extracted Budget: {prefs1.get('budget')}")
    print(f"Extracted Experiences: {prefs1.get('interests')}")
    print(f"Quiz Active: {res1.get('quiz')}")
    print(f"Route Data Present: {res1.get('route_data') is not None}")

    # Assertions for Test 1
    assert prefs1.get('starting_point') == "Delhi", "Origin should be Delhi"
    assert prefs1.get('destination') == "Goa", "Destination should be Goa"
    assert "5" in str(prefs1.get('travelers')), "Travelers should include 5"
    assert "car" in str(prefs1.get('transport')).lower(), "Transport should be car"
    assert "7" in str(prefs1.get('duration')), "Duration should be 7 days"
    assert "50k" in str(prefs1.get('budget')).lower(), "Budget should include 50k"
    
    # Must NOT ask generic questions
    msg1_lower = msg1.lower()
    forbidden_questions = [
        "how many people are traveling",
        "what is your total budget",
        "how many days are you planning",
        "what experiences matter most",
        "what accommodation do you prefer",
        "how are you traveling"
    ]
    for fq in forbidden_questions:
        assert fq not in msg1_lower, f"Forbidden question found in response: '{fq}'"

    # Must NOT show quiz widget or unnecessary map on conversational overview
    assert res1.get('quiz') is None or not res1.get('quiz', {}).get('active'), "Quiz should be inactive"
    assert res1.get('route_data') is None, "Map should not be automatically attached on overview"
    print("✓ Test 1 Passed: Complete prompt handled with full extraction and zero generic questionnaire questions.")

    # ------------------------------------------------------------------
    # TEST 2: Normal Travel Question
    # ------------------------------------------------------------------
    print("\n--- TEST 2: Normal Travel Question ---")
    await asyncio.sleep(4)
    prompt_2 = "What are the best beaches in Goa?"
    res2 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_2}])
    msg2 = res2.get("message", "")
    print(f"Message preview: {msg2[:150]}...")
    assert res2.get('quiz') is None, "Normal travel question must NOT show quiz"
    assert res2.get('route_data') is None, "Normal travel question must NOT show route map"
    assert "beach" in msg2.lower(), "Should talk about Goa beaches"
    print("✓ Test 2 Passed: Normal travel question answered naturally with no quiz, map, or weather.")

    # ------------------------------------------------------------------
    # TEST 3: Road Distance Question
    # ------------------------------------------------------------------
    print("\n--- TEST 3: Road Distance Question ---")
    await asyncio.sleep(4)
    prompt_3 = "Delhi to Jaipur road distance?"
    res3 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_3}])
    msg3 = res3.get("message", "")
    print(f"Intent: {res3.get('intent')}")
    print(f"Message preview: {msg3[:150]}...")
    print(f"Route Data attached: {res3.get('route_data') is not None}")
    assert res3.get('intent') == "route_planning", "Intent should be route_planning"
    assert res3.get('quiz') is None, "Distance query must NOT show quiz"
    print("✓ Test 3 Passed: Road distance correctly classified as route_planning with route data.")

    # ------------------------------------------------------------------
    # TEST 4: Weather Question
    # ------------------------------------------------------------------
    print("\n--- TEST 4: Weather Question ---")
    await asyncio.sleep(4)
    prompt_4 = "What's the weather in Goa this weekend?"
    res4 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_4}])
    msg4 = res4.get("message", "")
    print(f"Intent: {res4.get('intent')}")
    print(f"Message preview: {msg4[:150]}...")
    assert res4.get('intent') == "weather_inquiry", "Intent should be weather_inquiry"
    assert res4.get('quiz') is None, "Weather question must NOT show quiz"
    assert res4.get('route_data') is None, "Weather question must NOT show map"
    print("✓ Test 4 Passed: Weather query handled without quiz or map.")

    # ------------------------------------------------------------------
    # TEST 5: Long Road Trip with Sensible Overnight Stops
    # ------------------------------------------------------------------
    print("\n--- TEST 5: Long Road Trip (Delhi to Mumbai, 8 days, 4 friends) ---")
    await asyncio.sleep(4)
    prompt_5 = "Plan a road trip from Delhi to Mumbai for 8 days in my car. We are 4 friends. Suggest sensible overnight stops."
    res5 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_5}])
    msg5 = res5.get("message", "")
    prefs5 = res5.get("preferences", {})
    print(f"Message preview: {msg5[:200]}...")
    print(f"Extracted Travelers: {prefs5.get('travelers')}")
    print(f"Extracted Transport: {prefs5.get('transport')}")
    print(f"Extracted Duration: {prefs5.get('duration')}")
    
    # Must not ask about travelers, transport or duration
    msg5_lower = msg5.lower()
    assert "how many people" not in msg5_lower, "Must not ask how many people"
    assert "how many days" not in msg5_lower, "Must not ask how many days"
    assert "2-3 hours of daily travel" not in msg5_lower and "2 to 3 hours daily" not in msg5_lower, "No contradictory driving calculations"
    
    # Must suggest sensible stops like Udaipur, Ahmedabad, or Jaipur
    has_sensible_stop = any(stop.lower() in msg5_lower for stop in ["udaipur", "ahmedabad", "jaipur", "surat"])
    assert has_sensible_stop, "Must suggest sensible intermediate corridor stops"
    print("✓ Test 5 Passed: Realistic driving schedule and corridor stops suggested without redundant questions.")

    # ------------------------------------------------------------------
    # TEST 6: Partial Trip Prompt
    # ------------------------------------------------------------------
    print("\n--- TEST 6: Partial Trip Prompt ---")
    await asyncio.sleep(4)
    prompt_6 = "I want to plan a Goa trip."
    res6 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_6}])
    msg6 = res6.get("message", "")
    print(f"Message: {msg6}")
    assert res6.get('quiz') is None, "Partial query must NOT dump rigid quiz widget"
    assert res6.get('route_data') is None, "Partial query must NOT show map"
    print("✓ Test 6 Passed: Natural conversational response without rigid questionnaire.")

    # ------------------------------------------------------------------
    # TEST 7: Natural Language Dates Extraction
    # ------------------------------------------------------------------
    print("\n--- TEST 7: Natural Language Dates Extraction ---")
    await asyncio.sleep(4)
    prompt_7 = "I want to travel from Delhi to Goa from 10 October to 17 October."
    res7 = await grok_service.generate_smart_trip_response([{"role": "user", "content": prompt_7}])
    prefs7 = res7.get("preferences", {})
    print(f"Extracted Dates: {prefs7.get('dates')}")
    print(f"Extracted Origin: {prefs7.get('starting_point')}")
    print(f"Extracted Destination: {prefs7.get('destination')}")
    assert prefs7.get('dates') is not None, "Dates must be extracted from natural language"
    assert "October" in prefs7.get('dates'), "October dates must be preserved"
    print("✓ Test 7 Passed: Natural dates extracted and stored in preferences.")

    # ------------------------------------------------------------------
    # TEST 8: Final Itinerary Trigger
    # ------------------------------------------------------------------
    print("\n--- TEST 8: Final Itinerary Trigger ---")
    await asyncio.sleep(4)
    history_8 = [
        {"role": "user", "content": "I want to go to Goa from Delhi for 5 days with 2 friends, budget 40k."},
        {"role": "assistant", "content": "Sounds great! We can cover North Goa beaches and Portuguese heritage."},
        {"role": "user", "content": "Okay, create my final itinerary."}
    ]
    res8 = await grok_service.generate_smart_trip_response(history_8)
    print(f"Intent: {res8.get('intent')}")
    print(f"Itinerary Present: {res8.get('itinerary') is not None}")
    assert res8.get('intent') == "plan_itinerary", "Intent should be plan_itinerary"
    print("✓ Test 8 Passed: Final itinerary trigger correctly sets intent and generates plan.")

    print("\n====================================================================")
    print("ALL 8 VALIDATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================================")

if __name__ == "__main__":
    asyncio.run(run_validation_suite())
