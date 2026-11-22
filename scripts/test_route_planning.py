#!/usr/bin/env python3
import sys
import os
import asyncio
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.map_service import map_service

async def test_kashmir_route_planning():
    print("=== Testing SmartTrip Interactive Maps & Route Planning ===")
    
    origin = "Delhi"
    stops = ["Srinagar", "Sonamarg", "Gulmarg"]
    
    print(f"Origin: {origin}")
    print(f"Stops: {', '.join(stops)}\n")
    
    print("Planning road route with Nominatim Geocoding + OSRM Driving Machine...")
    result = await map_service.plan_route(origin, stops)
    
    print("\n--- Route Plan Summary ---")
    print(f"Status: {result['status']}")
    print(f"Origin Resolved: {result['origin']['display_name']} ({result['origin']['lat']}, {result['origin']['lon']})")
    
    print("\nResolved Destinations:")
    for idx, stop in enumerate(result['stops'], 1):
        print(f"  Stop {idx}: {stop['display_name']} ({stop['lat']}, {stop['lon']})")
        
    print("\nSequential Route Legs:")
    for idx, leg in enumerate(result['legs'], 1):
        print(f"  Leg {idx}: {leg['from_name']} ➔ {leg['to_name']}")
        print(f"         Distance: {leg['distance_km']} km | Driving Duration: {leg['duration_text']} ({leg['duration_minutes']} mins)")
        
    print("\nOverall Route Totals:")
    print(f"  Total Distance: {result['total_distance_km']} km")
    print(f"  Total Duration: {result['total_duration_text']} ({result['total_duration_minutes']} mins)")
    print(f"  Polyline Coordinates Points: {len(result['geometry'])} points")
    print(f"\nGoogle Maps Navigation URL:\n{result['google_maps_url']}")

    # Verifications
    assert result['origin']['name'].lower() == "delhi", "Origin not geocoded to Delhi"
    assert len(result['stops']) == 3, "Stops count mismatch"
    assert len(result['legs']) == 3, "Legs count mismatch"
    assert result['total_distance_km'] > 0, "Total distance should be greater than 0"
    assert result['total_duration_minutes'] > 0, "Total duration should be greater than 0"
    assert len(result['geometry']) > 0, "Polyline geometry points missing"
    assert "google.com/maps/dir" in result['google_maps_url'], "Google Maps link missing"

    print("\n✅ TEST PASSED: All locations geocoded, road legs calculated, polyline generated, and Google Maps action ready!")

if __name__ == "__main__":
    asyncio.run(test_kashmir_route_planning())
