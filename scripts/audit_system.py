import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import json
import traceback
from dotenv import load_dotenv

load_dotenv()

async def audit_all():
    results = {}
    print("========================================")
    print("STARTING FULL SYSTEM AUDIT")
    print("========================================")

    # 1. Weather Service
    print("\n--- 1. Testing Weather Service (Open-Meteo) ---")
    try:
        from backend.services.weather_service import weather_service
        w_city = await weather_service.get_weather_for_city("Delhi")
        w_eval = await weather_service.evaluate_travel_weather("Goa", "10 Oct to 15 Oct")
        results["weather_service"] = {
            "status": "WORKING",
            "delhi_weather": w_city.get("weather_condition"),
            "delhi_temp": w_city.get("current_temperature_c"),
            "goa_season": w_eval.get("season_name") if w_eval else None,
            "goa_summary": w_eval.get("climate_summary") if w_eval else None
        }
        print(" [OK] Weather Service:", results["weather_service"])
    except Exception as e:
        results["weather_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Weather Service:", e)

    # 2. Geocoding & Map / Routing Service (OSRM / Nominatim)
    print("\n--- 2. Testing Geocoding & Map Service (OSRM / Nominatim) ---")
    try:
        from backend.services.geocoding_service import geocoding_service
        from backend.services.map_service import map_service
        geo = await geocoding_service.geocode("Delhi")
        route = await map_service.plan_route("Delhi", ["Goa"])
        results["map_service"] = {
            "status": "WORKING",
            "delhi_coords": [geo.get("lat"), geo.get("lon")] if geo else None,
            "route_found": route.get("status") if route else None,
            "total_km": route.get("total_distance_km") if route else None,
            "duration": route.get("total_duration_text") if route else None,
            "geometry_present": bool(route.get("geometry")) if route else False
        }
        print(" [OK] Map Service:", results["map_service"])
    except Exception as e:
        results["map_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Map Service:", e)

    # 3. Tourism Service
    print("\n--- 3. Testing Tourism Service (CSV dataset) ---")
    try:
        from backend.services.tourism_service import tourism_service
        dests = tourism_service.search_destinations("Goa", limit=3)
        sample = dests[0] if dests else None
        results["tourism_service"] = {
            "status": "WORKING",
            "total_destinations_search": len(dests),
            "sample_destination": sample["destination_name"] if sample else None,
            "sample_state": sample["state"] if sample else None,
            "sample_category": sample["category"] if sample else None
        }
        print(" [OK] Tourism Service:", results["tourism_service"])
    except Exception as e:
        results["tourism_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Tourism Service:", e)

    # 4. Recommendation Engine
    print("\n--- 4. Testing Recommendation Engine ---")
    try:
        from backend.recommendation.engine import recommendation_engine
        rec_res = recommendation_engine.recommend(
            trip_context={
                "destination": "Goa",
                "starting_point": "Delhi",
                "transport": "Car (Self-drive)",
                "duration": "7 days",
                "interests": ["Beaches & Relaxation"]
            },
            top_n=5
        )
        results["recommendation_engine"] = {
            "status": "WORKING",
            "total_recs": len(rec_res.get("recommendations", [])),
            "intermediate_stops": rec_res.get("intermediate_stops", []),
            "top_rec": rec_res.get("recommendations", [])[0]["name"] if rec_res.get("recommendations") else None
        }
        print(" [OK] Recommendation Engine:", results["recommendation_engine"])
    except Exception as e:
        results["recommendation_engine"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Recommendation Engine:", e)

    # 5. Landmark Service (ResNet-18)
    print("\n--- 5. Testing Landmark Recognition Service (ResNet-18) ---")
    try:
        from backend.services.landmark_service import landmark_service
        results["landmark_service"] = {
            "status": "WORKING" if landmark_service.is_loaded else "NOT_LOADED",
            "is_loaded": landmark_service.is_loaded,
            "num_classes": landmark_service.num_classes,
            "device": str(landmark_service.device),
            "sample_classes": landmark_service.class_names[:5] if landmark_service.class_names else []
        }
        print(" [OK] Landmark Service:", results["landmark_service"])
    except Exception as e:
        results["landmark_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Landmark Service:", e)

    # 6. Scene Recognition Service (Places365)
    print("\n--- 6. Testing Scene Recognition Service (Places365) ---")
    try:
        from backend.services.scene_service import scene_service
        status_info = scene_service.get_model_status()
        results["scene_service"] = {
            "status": "WORKING" if status_info.get("model_loaded") else "NOT_LOADED",
            "model_status": status_info
        }
        print(" [OK] Scene Service:", results["scene_service"])
    except Exception as e:
        results["scene_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Scene Service:", e)

    # 7. Visual Similarity Service (FAISS)
    print("\n--- 7. Testing Visual Similarity Service (FAISS) ---")
    try:
        from backend.services.visual_similarity_service import visual_similarity_service
        status_info = visual_similarity_service.get_status()
        results["visual_similarity_service"] = {
            "status": "WORKING" if status_info.get("ready") else "NOT_READY",
            "status_details": status_info
        }
        print(" [OK] Visual Similarity Service:", results["visual_similarity_service"])
    except Exception as e:
        results["visual_similarity_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Visual Similarity Service:", e)

    # 8. Train Service (RailKit)
    print("\n--- 8. Testing Train Service (RailKit / Bridge) ---")
    try:
        from backend.services.train_service import train_service
        train_res = await train_service.search_trains("Delhi", "Goa", limit=3)
        results["train_service"] = {
            "status": "WORKING",
            "api_status": train_res.get("status"),
            "total_trains": train_res.get("total_trains"),
            "sample_train": train_res.get("trains", [])[0] if train_res.get("trains") else None
        }
        print(" [OK] Train Service:", results["train_service"])
    except Exception as e:
        results["train_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Train Service:", e)

    # 9. Flight Service (SerpApi Google Flights)
    print("\n--- 9. Testing Flight Service (SerpApi Google Flights) ---")
    try:
        from backend.services.flight_service import flight_service
        flight_res = await flight_service.search_flights("Delhi", "Goa", limit=3)
        results["flight_service"] = {
            "status": "WORKING",
            "api_status": flight_res.get("status"),
            "total_flights": flight_res.get("total_flights"),
            "sample_flight": flight_res.get("flights", [])[0] if flight_res.get("flights") else None
        }
        print(" [OK] Flight Service:", results["flight_service"])
    except Exception as e:
        results["flight_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Flight Service:", e)

    # 10. Hotel Service (Makcorps Free API)
    print("\n--- 10. Testing Hotel Service (Makcorps Free API) ---")
    try:
        from backend.services.hotel_service import hotel_service
        hotel_res = await hotel_service.search_hotels("Goa", limit=3)
        results["hotel_service"] = {
            "status": "WORKING",
            "api_status": hotel_res.get("status"),
            "total_hotels": hotel_res.get("total_hotels"),
            "sample_hotel": hotel_res.get("hotels", [])[0] if hotel_res.get("hotels") else None
        }
        print(" [OK] Hotel Service:", results["hotel_service"])
    except Exception as e:
        results["hotel_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Hotel Service:", e)

    # 11. Trip Storage & Journal Storage
    print("\n--- 11. Testing Trip & Journal Storage Services ---")
    try:
        from backend.services.trip_storage_service import trip_storage_service
        from backend.services.journal_storage_service import journal_storage_service
        trips = trip_storage_service.list_trips()
        posts = journal_storage_service.list_posts()
        results["storage_services"] = {
            "status": "WORKING",
            "saved_trips_count": len(trips),
            "journal_posts_count": len(posts)
        }
        print(" [OK] Storage Services:", results["storage_services"])
    except Exception as e:
        results["storage_services"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Storage Services:", e)

    # 12. PDF Export Service
    print("\n--- 12. Testing PDF Service ---")
    try:
        from backend.services.pdf_service import generate_itinerary_pdf
        dummy_itinerary = {
            "overview": {"title": "Goa Trip", "destination": "Goa", "origin": "Delhi", "duration": "5 Days"},
            "days": [{"day": 1, "destination": "Goa", "morning": "Arrive and check in", "afternoon": "Beach", "evening": "Dinner", "stay_area": "Panaji"}]
        }
        pdf_bytes = generate_itinerary_pdf(dummy_itinerary)
        results["pdf_service"] = {
            "status": "WORKING",
            "pdf_size_bytes": len(pdf_bytes) if pdf_bytes else 0
        }
        print(" [OK] PDF Service:", results["pdf_service"])
    except Exception as e:
        results["pdf_service"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] PDF Service:", e)

    # 13. Grok / Groq LLM Assistant Chat Integration
    print("\n--- 13. Testing Grok/Groq LLM Assistant Service ---")
    try:
        from backend.services.grok_service import grok_service
        grok_res = await grok_service.generate_smart_trip_response(
            messages=[{"role": "user", "content": "Delhi to Goa by car"}]
        )
        results["grok_service_delhi_goa"] = {
            "status": "WORKING",
            "intent": grok_res.get("intent"),
            "preferences": grok_res.get("preferences"),
            "itinerary_present": bool(grok_res.get("itinerary")),
            "route_data_present": bool(grok_res.get("route_data")),
            "message_snippet": grok_res.get("message", "")[:300]
        }
        print(" [OK] Grok Service (Delhi to Goa by car):", results["grok_service_delhi_goa"])
    except Exception as e:
        results["grok_service_delhi_goa"] = {"status": "FAILED", "error": str(e), "traceback": traceback.format_exc()}
        print(" [FAIL] Grok Service:", e)

    with open("scripts/audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nAudit saved to scripts/audit_results.json")

if __name__ == "__main__":
    asyncio.run(audit_all())
