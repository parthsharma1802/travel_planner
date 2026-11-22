import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def run_query_tests():
    from backend.services.grok_service import grok_service
    test_cases = [
        {
            "name": "Query 1: Minimal road trip prompt",
            "messages": [{"role": "user", "content": "Delhi to Goa by car"}]
        },
        {
            "name": "Query 2: Complete road trip with budget & duration",
            "messages": [{"role": "user", "content": "I am from Delhi and want to drive to Goa with 4 friends in my car for 7 days, budget 50k, interested in beaches & nightlife"}]
        },
        {
            "name": "Query 3: Train journey direct",
            "messages": [{"role": "user", "content": "Delhi to Kolkata by train for 5 days"}]
        },
        {
            "name": "Query 4: Pure informational query (non-trip intake)",
            "messages": [{"role": "user", "content": "What is Jaipur famous for?"}]
        },
        {
            "name": "Query 5: Direct trip without stops",
            "messages": [{"role": "user", "content": "Plan a direct 5-day trip to Goa from Delhi by flight, no intermediate stops"}]
        },
        {
            "name": "Query 6: Multi-turn conversation detail update",
            "messages": [
                {"role": "user", "content": "I want to plan a trip to Goa for 5 days from Delhi with 4 friends"},
                {"role": "assistant", "content": "Sounds great! Are you planning to drive, take a train, or fly?"},
                {"role": "user", "content": "Actually we are 3 friends now instead of 4, and we want to go by car"}
            ]
        }
    ]

    results = []
    for tc in test_cases:
        print(f"\n========================================\nRunning {tc['name']}")
        res = await grok_service.generate_smart_trip_response(
            messages=tc["messages"]
        )
        summary = {
            "name": tc["name"],
            "intent": res.get("intent"),
            "preferences": res.get("preferences"),
            "route_data_present": bool(res.get("route_data")),
            "itinerary_present": bool(res.get("itinerary")),
            "train_data_present": bool(res.get("train_data")),
            "flight_data_present": bool(res.get("flight_data")),
            "hotel_data_present": bool(res.get("hotel_data")),
            "recommendations_count": len(res.get("recommendations", [])) if res.get("recommendations") else 0,
            "response_message": res.get("message")
        }
        results.append(summary)
        print(f"Intent: {summary['intent']}")
        print(f"Preferences: {json.dumps(summary['preferences'])}")
        print(f"Response:\n{summary['response_message']}\n")

    with open("scripts/query_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(run_query_tests())
