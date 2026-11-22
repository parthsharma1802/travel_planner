#!/usr/bin/env python3
import sys
import os
import asyncio
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.grok_service import grok_service

async def run_scenario_tests():
    print("=== Testing India-Focused Conversational Quiz & Structured Trip Context ===\n")

    scenarios = [
        {
            "name": "Scenario 1: Delhi -> Mumbai Road Trip with Friends",
            "messages": [
                {"role": "user", "content": "Delhi to Mumbai road trip with friends for 5 days"}
            ]
        },
        {
            "name": "Scenario 2: Varanasi -> Ayodhya -> Prayagraj Spiritual Trip",
            "messages": [
                {"role": "user", "content": "Varanasi to Ayodhya and Prayagraj spiritual pilgrimage trip"}
            ]
        },
        {
            "name": "Scenario 3: Family Trip to Rajasthan Focused on Heritage and Culture",
            "messages": [
                {"role": "user", "content": "Family trip to Rajasthan for 6 days focused on heritage and culture"}
            ]
        },
        {
            "name": "Scenario 4: Solo Himalayan Trip Focused on Nature and Spirituality",
            "messages": [
                {"role": "user", "content": "Solo trip to Shimla and Manali focused on nature, mountains and meditative spirituality"}
            ]
        }
    ]

    for idx, sc in enumerate(scenarios, 1):
        print(f"==================================================")
        print(f"RUNNING {sc['name']}")
        print(f"User Prompt: '{sc['messages'][0]['content']}'")
        print(f"==================================================")
        
        result = await grok_service.generate_smart_trip_response(sc["messages"])
        
        print("\n--- EXTRACTED STRUCTURED TRIP CONTEXT (preferences) ---")
        print(json.dumps(result["preferences"], indent=2))

        print(f"\nIntent Detected: {result['intent']}")
        print(f"Quiz Active: {bool(result.get('quiz'))}")
        
        if result.get("route_data"):
            rd = result["route_data"]
            print(f"Route Detected: {rd['origin']['name']} -> {[s['name'] for s in rd['stops']]} ({rd['total_distance_km']} km, {rd['total_duration_text']})")

        print("\n--- SAMPLE CONVERSATIONAL ANSWER SNIPPET ---")
        print(result["message"][:350] + "...\n")
        
        # Verifications
        assert result["status"] == "success", f"Scenario {idx} failed"
        assert result["preferences"]["destination"] is not None, f"Destination not extracted in Scenario {idx}"

        # 15-second delay between scenarios to respect Groq 8,000 TPM rate limit
        if idx < len(scenarios):
            print("Sleeping 15 seconds to respect Groq 8000 TPM rate limit...\n")
            await asyncio.sleep(15)

    print("✅ ALL 4 SCENARIOS PASSED: Structured trip context correctly extracted and stored across all travel types!")

if __name__ == "__main__":
    asyncio.run(run_scenario_tests())
