import os
import sys
import asyncio
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.services.hotel_service import hotel_service
from backend.services.grok_service import grok_service

client = TestClient(app)

def run_tests():
    print("=== 1. TESTING REST ENDPOINT GET /api/hotels/search?city=Kolkata ===")
    res = client.get("/api/hotels/search?city=Kolkata&limit=4")
    print("HTTP Status:", res.status_code)
    data = res.json()
    print("Status:", data.get("status"))
    print("Source:", data.get("source"))
    print("City:", data.get("city"))
    print("Total Hotels:", data.get("total_hotels"))
    print("\nParsed Hotels (Sorted by Lowest Indicative Rate):")
    for h in data.get("hotels", []):
        name = h.get("hotel_name")
        p_inr = h.get("lowest_price_inr")
        p_usd = h.get("lowest_price_usd")
        vendor = h.get("best_vendor")
        print(f"  - {name}: Indicative ₹{p_inr:,} (${p_usd}) on {vendor}")
        for v in h.get("vendor_offers", []):
            v_name = v.get("vendor")
            v_usd = v.get("price_usd")
            v_tax = v.get("tax_usd")
            v_inr = v.get("price_inr")
            print(f"      * {v_name}: ${v_usd} (₹{v_inr:,}) + Tax: ${v_tax}")

    print("\n=== 2. TESTING JWT BACKEND-ONLY ISOLATION ===")
    raw_str = json.dumps(data).lower()
    is_jwt_leaked = "jwt " in raw_str or "eyj" in raw_str or "token" in data
    print("Is JWT exposed in API response?:", is_jwt_leaked)
    assert not is_jwt_leaked, "JWT token leaked in response!"

    print("\n=== 3. TESTING ERROR HANDLING (EMPTY / INVALID CITY) ===")
    err_res = client.get("/api/hotels/search?city=")
    print("Empty city response status code:", err_res.status_code)
    assert err_res.status_code == 400, "Should return 400 for empty city"

    print("\n=== 4. TESTING CHATBOT INTEGRATION WITH BUDGET QUERY (KOLKATA) ===")
    async def run_chat():
        chat_res = await grok_service.generate_smart_trip_response(
            messages=[{"role": "user", "content": "₹10,000 budget mein 5 din Kolkata ke liye stay options batao"}]
        )
        print(chat_res.get("message"))

    asyncio.run(run_chat())

if __name__ == "__main__":
    run_tests()
