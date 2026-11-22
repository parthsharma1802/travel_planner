import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def run_orchestration_tests():
    from backend.services.grok_service import grok_service
    test_cases = [
        {
            "id": 1,
            "title": "Test 1: Image -> Landmark -> Nearby Recommendations",
            "messages": [{"role": "user", "content": "I took this photo while traveling. Can you tell me what it is and what to do nearby?"}],
            "landmark_context": {
                "landmark_name": "Taj Mahal",
                "location": "Agra, Uttar Pradesh",
                "confidence_level": "high",
                "tourism_info": {
                    "description": "Iconic 17th-century ivory-white marble mausoleum on the south bank of the Yamuna river.",
                    "category": "Historical Monument"
                }
            }
        },
        {
            "id": 2,
            "title": "Test 2: Delhi -> Goa by car",
            "messages": [{"role": "user", "content": "Delhi to Goa by car"}]
        },
        {
            "id": 3,
            "title": "Test 3: Delhi -> Goa with a limited budget",
            "messages": [{"role": "user", "content": "I want to plan a 5-day trip from Delhi to Goa with my friend on a tight budget of ₹15,000 total"}]
        },
        {
            "id": 4,
            "title": "Test 4: Flight vs Train vs Car Comparison",
            "messages": [{"role": "user", "content": "Compare flight vs train vs car from Delhi to Goa for 2 people"}]
        },
        {
            "id": 5,
            "title": "Test 5: Hotel Recommendation within Budget",
            "messages": [{"role": "user", "content": "Suggest hotels to stay in Goa for 4 nights, my total hotel budget is around ₹6,000 to ₹8,000"}]
        }
    ]

    print("================================================================")
    print("RUNNING INTELLIGENT ORCHESTRATION VERIFICATION TESTS")
    print("================================================================")

    results = []
    for tc in test_cases:
        print(f"\n----------------------------------------------------------------")
        print(f"Executing {tc['title']}")
        print(f"----------------------------------------------------------------")
        res = await grok_service.generate_smart_trip_response(
            messages=tc["messages"],
            landmark_context=tc.get("landmark_context")
        )
        print(f"Intent: {res.get('intent')}")
        print(f"Route Attached: {bool(res.get('route_data'))}")
        print(f"Trains Attached: {bool(res.get('train_data'))}")
        print(f"Flights Attached: {bool(res.get('flight_data'))}")
        print(f"Hotels Attached: {bool(res.get('hotel_data'))}")
        print(f"Recommendations Attached: {bool(res.get('recommendations'))}")
        print(f"\nResponse Output:\n{res.get('message')}\n")

        results.append({
            "id": tc["id"],
            "title": tc["title"],
            "intent": res.get("intent"),
            "has_route": bool(res.get("route_data")),
            "has_trains": bool(res.get("train_data")),
            "has_flights": bool(res.get("flight_data")),
            "has_hotels": bool(res.get("hotel_data")),
            "has_recommendations": bool(res.get("recommendations")),
            "message": res.get("message")
        })

    with open("scripts/orchestration_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nAll tests completed! Saved to scripts/orchestration_results.json")

if __name__ == "__main__":
    asyncio.run(run_orchestration_tests())
