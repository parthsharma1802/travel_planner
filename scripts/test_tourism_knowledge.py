#!/usr/bin/env python3
import sys
import os
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.tourism_service import tourism_service

def test_rajasthan_historical_query():
    print("=== Testing Tourism Knowledge Layer Dataset Retrieval ===")
    
    # Test Query requested by user
    query = "historical"
    state = "Rajasthan"
    
    print(f"Querying dataset for: state='{state}', query='{query}'...")
    results = tourism_service.search_destinations(query=query, state=state, limit=5)
    
    print(f"Retrieved {len(results)} records from data/processed/tourism_master.csv:\n")
    
    for idx, r in enumerate(results, 1):
        print(f"{idx}. {r['destination_name']} | District: {r['city_district']} | Category: {r['category']} | Rating: {r.get('rating') or 'N/A'}")
        if r.get('description'):
            print(f"   Desc: {r['description'][:100]}...")
        print("-" * 60)

    assert len(results) > 0, "No records returned for Rajasthan historical destinations query!"
    print("✅ TEST PASSED: Tourism Master Dataset successfully returned relevant Rajasthan records!")

if __name__ == "__main__":
    test_rajasthan_historical_query()
