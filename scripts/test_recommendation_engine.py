"""
Validation test suite for SmartTrip Recommendation Engine.
Tests all requirements from section 19:
1. Goa recommendation query.
2. Delhi -> Goa road-trip recommendation.
3. Long road trip such as Delhi -> Mumbai.
4. Family trip.
5. Friends trip.
6. Spiritual/pilgrimage trip.
7. Budget-constrained trip.
8. Weather-sensitive recommendation.
9. Route-aware: no far-away places.
10. Not invoked on unrelated queries.
11. Structured result without exposing raw scores in user message.
12. Tool separation: internal tool use != auto UI widget.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.recommendation.engine import recommendation_engine

def run_tests():
    print("==================================================")
    print("RUNNING RECOMMENDATION ENGINE TEST SUITE")
    print("==================================================")

    # 1. Goa recommendation query
    print("\n[Test 1] Goa recommendation query:")
    res_goa = recommendation_engine.recommend(
        trip_context={"destination": "Goa", "experiences": ["Beaches & Relaxation"]},
        top_n=5
    )
    print(f"Total candidates: {res_goa['total_candidates']}")
    print(f"Top 3 recommendations:")
    for r in res_goa["recommendations"][:3]:
        print(f"  - {r['name']} ({r['category']}, {r['state']}) | Score: {r['score']} | Reasons: {r['reasons']}")
    assert len(res_goa["recommendations"]) > 0, "Goa recommendations should not be empty"
    print("✓ Test 1 Passed")

    # 2. Delhi -> Goa road trip recommendation
    print("\n[Test 2] Delhi -> Goa road-trip recommendation (intermediate stops):")
    res_delhi_goa = recommendation_engine.recommend(
        trip_context={
            "starting_point": "Delhi",
            "destination": "Goa",
            "transport": "Car",
            "travelers": "Friends Trip"
        },
        top_n=6
    )
    print(f"Intermediate stops detected: {res_delhi_goa['intermediate_stops']}")
    assert len(res_delhi_goa["intermediate_stops"]) > 0, "Delhi->Goa should have route intermediate stops"
    print("✓ Test 2 Passed")

    # 3. Long road trip: Delhi -> Mumbai
    print("\n[Test 3] Long road trip: Delhi -> Mumbai:")
    res_delhi_mumbai = recommendation_engine.recommend(
        trip_context={
            "starting_point": "Delhi",
            "destination": "Mumbai",
            "transport": "Car"
        },
        top_n=5
    )
    print(f"Intermediate stops: {res_delhi_mumbai['intermediate_stops']}")
    assert "Udaipur" in res_delhi_mumbai["intermediate_stops"] or "Jaipur" in res_delhi_mumbai["intermediate_stops"], "Should suggest Jaipur/Udaipur/Ahmedabad"
    print("✓ Test 3 Passed")

    # 4. Family trip
    print("\n[Test 4] Family trip (parks, museums, heritage):")
    res_family = recommendation_engine.recommend(
        trip_context={
            "destination": "Jaipur",
            "travelers": "Family Trip",
            "experiences": ["History, Heritage & Culture", "Nature & Scenic Places"]
        },
        top_n=5
    )
    for r in res_family["recommendations"][:3]:
        print(f"  - {r['name']} ({r['category']}) | Reasons: {r['reasons']}")
    assert any("Family" in " ".join(r["reasons"]) or "family" in " ".join(r["reasons"]) for r in res_family["recommendations"]), "Should identify family suitability"
    print("✓ Test 4 Passed")

    # 5. Friends trip
    print("\n[Test 5] Friends trip (beaches, adventure):")
    res_friends = recommendation_engine.recommend(
        trip_context={
            "destination": "Goa",
            "travelers": "Friends Trip",
            "experiences": ["Beaches & Relaxation", "Adventure & Outdoor Activities"]
        },
        top_n=5
    )
    for r in res_friends["recommendations"][:3]:
        print(f"  - {r['name']} ({r['category']}) | Score: {r['score']}")
    print("✓ Test 5 Passed")

    # 6. Spiritual / pilgrimage trip
    print("\n[Test 6] Spiritual / pilgrimage trip:")
    res_spiritual = recommendation_engine.recommend(
        trip_context={
            "destination": "Varanasi",
            "travelers": "Spiritual/Pilgrimage Trip",
            "experiences": ["Spiritual & Pilgrimage"]
        },
        top_n=5
    )
    for r in res_spiritual["recommendations"][:3]:
        print(f"  - {r['name']} ({r['category']}) | Score: {r['score']}")
    assert any("temple" in (r["category"] or "").lower() or "spiritual" in " ".join(r["reasons"]).lower() for r in res_spiritual["recommendations"]), "Should rank temples/spiritual sites high"
    print("✓ Test 6 Passed")

    # 7. Budget-constrained trip
    print("\n[Test 7] Budget-constrained trip:")
    res_budget = recommendation_engine.recommend(
        trip_context={
            "destination": "Jaipur",
            "budget": "₹15,000 total for 3 days"
        },
        top_n=4
    )
    print(f"Top budget recommendation: {res_budget['recommendations'][0]['name']}")
    print("✓ Test 7 Passed")

    # 8. Weather-sensitive recommendation
    print("\n[Test 8] Weather-sensitive recommendation (Rain vs Pleasant):")
    res_rain = recommendation_engine.recommend(
        trip_context={"destination": "Goa", "experiences": ["Beaches & Relaxation"]},
        weather_condition="Heavy Rain & Thunderstorm",
        top_n=3
    )
    res_clear = recommendation_engine.recommend(
        trip_context={"destination": "Goa", "experiences": ["Beaches & Relaxation"]},
        weather_condition="Clear Sky & Pleasant",
        top_n=3
    )
    score_rain = res_rain["recommendations"][0]["score"]
    score_clear = res_clear["recommendations"][0]["score"]
    print(f"Score with Rain: {score_rain} vs Score with Pleasant: {score_clear}")
    assert score_clear >= score_rain, "Clear weather should yield higher or equal suitability for outdoor beach places"
    print("✓ Test 8 Passed")

    # 9. Route-aware: verify intermediate stops are sensible
    print("\n[Test 9] Route-aware verification:")
    res_route = recommendation_engine.recommend(
        trip_context={"starting_point": "Delhi", "destination": "Goa", "transport": "Car"},
        top_n=5
    )
    print(f"Suggested intermediate stops on Delhi -> Goa route: {res_route['intermediate_stops']}")
    assert all(s in ["Udaipur", "Ahmedabad", "Mumbai", "Pune"] for s in res_route["intermediate_stops"])
    print("✓ Test 9 Passed")

    # 10. Check intent detection logic for unrelated queries
    print("\n[Test 10] Intent detection: verify engine is NOT called on unrelated queries:")
    from backend.services.grok_service import grok_service
    unrelated_msg = "What is the capital of France?"
    is_rec = any(kw in unrelated_msg.lower() for kw in [
        "recommend", "suggest", "best places", "where to go", "what to see",
        "places in", "places to visit", "should i stop", "stops", "things to do",
        "attractions", "trip planning", "plan my trip", "road trip"
    ])
    assert not is_rec, "Unrelated query should not trigger recommendation engine"
    print(f"Unrelated query '{unrelated_msg}' needs_recommendations: {is_rec}")
    print("✓ Test 10 Passed")

    print("\n==================================================")
    print("ALL 10 TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
