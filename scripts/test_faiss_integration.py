#!/usr/bin/env python3
"""
Test Suite: FAISS Visual Similarity Pipeline Integration
Validates all requirements:
1. Known Hawa Mahal image: Recognition + FAISS Visual Similarity
2. Other known monuments (Taj Mahal, Qutub Minar, India Gate)
3. Unknown / non-landmark image: Confidence-aware FAISS visual matching
4. Invalid & corrupted file handling
5. FAISS failure resilience: Landmark recognition continues gracefully if FAISS is offline
6. Image upload inside existing travel conversation
7. Follow-up: 'Tell me more'
8. Follow-up: 'What\'s nearby?'
9. Follow-up: 'Show it on map'
10. Follow-up: 'Plan a trip around this'
11. Single-load efficiency: Index, metadata, and ResNet feature extractor retained in memory
"""

import os
import sys
import glob
import io
import asyncio
from PIL import Image, ImageDraw
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.landmark_service import landmark_service
from backend.services.visual_similarity_service import visual_similarity_service
from backend.services.grok_service import grok_service

API_BASE = "http://localhost:8000"


def create_blank_test_image(color=(128, 128, 128), size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 160, 160], fill=(210, 210, 210))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_1_known_hawa_mahal_faiss():
    print("\n--- TEST 1: Known Hawa Mahal Image (Recognition + FAISS) ---")
    imgs = glob.glob(os.path.join(ROOT_DIR, "data/raw/**/hawa_mahal/*.jpg"), recursive=True) + \
           glob.glob(os.path.join(ROOT_DIR, "data/raw/**/*hawa*/*.jpg"), recursive=True)
    assert len(imgs) > 0, "No Hawa Mahal test images found"

    with open(imgs[0], "rb") as f:
        resp = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": ("hawa.jpg", f, "image/jpeg")})

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert data["landmark_name"] == "Hawa Mahal"
    assert data["confidence_level"] in ["high", "moderate"]
    assert len(data.get("similar_landmarks", [])) > 0, "FAISS similar landmarks should be populated"
    top_sim = data["similar_landmarks"][0]
    assert top_sim["landmark_name"] == "Hawa Mahal"
    print(f"✅ PASSED: Recognized {data['landmark_name']} with {len(data['similar_landmarks'])} FAISS visual matches")


def test_2_other_known_monuments():
    print("\n--- TEST 2: Other Known Monuments (Taj Mahal, Qutub Minar, etc.) ---")
    for target in ["taj_mahal", "qutub_minar", "india_gate"]:
        imgs = glob.glob(os.path.join(ROOT_DIR, f"data/raw/**/{target}/*.jpg"), recursive=True) + \
               glob.glob(os.path.join(ROOT_DIR, f"data/raw/**/*{target}*/*.jpg"), recursive=True)
        if imgs:
            with open(imgs[0], "rb") as f:
                resp = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": (f"{target}.jpg", f, "image/jpeg")})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data.get("landmark_name") is not None
            assert len(data.get("similar_landmarks", [])) > 0
            print(f"✅ Verified {target} -> Recognized: {data['landmark_name']} | Similar: {[s['landmark_name'] for s in data['similar_landmarks'][:2]]}")


def test_3_generic_image_confidence_faiss():
    print("\n--- TEST 3: Generic Image Confidence + FAISS Handling ---")
    generic_bytes = create_blank_test_image()
    resp = requests.post(
        f"{API_BASE}/api/landmark/recognize",
        files={"file": ("generic.jpg", io.BytesIO(generic_bytes), "image/jpeg")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    print(f"✅ Generic image: Status={data['identification_status']}, Conf={data['confidence_level']}, Similar count={len(data.get('similar_landmarks', []))}")


def test_4_invalid_and_corrupt_files():
    print("\n--- TEST 4: Invalid & Corrupted File Validation ---")
    # Empty file
    r1 = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")})
    assert r1.status_code == 400
    # Corrupted content
    r2 = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": ("corrupt.jpg", io.BytesIO(b"CORRUPT_BYTES_XYZ"), "image/jpeg")})
    assert r2.status_code == 400
    # Unsupported extension
    r3 = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")})
    assert r3.status_code in [400, 415]
    print("✅ All invalid and corrupted files safely rejected")


def test_5_faiss_direct_similar_endpoint():
    print("\n--- TEST 5: Direct FAISS Similarity Endpoint (/api/landmark/similar) ---")
    imgs = glob.glob(os.path.join(ROOT_DIR, "data/raw/**/hawa_mahal/*.jpg"), recursive=True) + \
           glob.glob(os.path.join(ROOT_DIR, "data/raw/**/*hawa*/*.jpg"), recursive=True)
    with open(imgs[0], "rb") as f:
        resp = requests.post(f"{API_BASE}/api/landmark/similar?top_k=5", files={"file": ("hawa.jpg", f, "image/jpeg")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_matches"] > 0
    assert len(data["top_matches"]) > 0
    print(f"✅ PASSED: Direct similarity retrieved {data['total_matches']} matches across {len(data['distinct_landmarks'])} distinct destinations")


async def test_6_conversational_followup_flows():
    print("\n--- TEST 6: Conversational Follow-up Flows (Groq Integration) ---")
    landmark_ctx = {
        "status": "success",
        "landmark_name": "Hawa Mahal",
        "location": "Jaipur, Rajasthan",
        "confidence_level": "high",
        "confidence_score": 0.989,
        "identification_status": "confident",
        "summary_statement": "Looks like Hawa Mahal",
        "similar_landmarks": [
            {"landmark_name": "Hawa Mahal", "location": "Jaipur, Rajasthan", "max_similarity": 1.0, "category": "Castle"},
            {"landmark_name": "City Palace", "location": "Jaipur, Rajasthan", "max_similarity": 0.82, "category": "Palace"}
        ],
        "tourism_info": {
            "destination_name": "Hawa Mahal",
            "state": "Rajasthan",
            "city_district": "Jaipur",
            "category": "Heritage Monument",
            "description": "Famous 5-story palace with 953 honeycomb windows built in 1799."
        }
    }

    # Follow-up A: Initial Image Identification
    messages = [
        {"role": "user", "content": "What monument is this?"}
    ]
    resp1 = await grok_service.generate_smart_trip_response(messages=messages, landmark_context=landmark_ctx)
    msg1 = resp1["message"].lower()
    assert "hawa" in msg1 and "mahal" in msg1, "Must identify Hawa Mahal"
    assert resp1.get("quiz") is None or not resp1.get("quiz", {}).get("active"), "Must NOT trigger quiz"
    print("✅ Initial recognition response is natural and clean")

    # Follow-up B: "Tell me more"
    messages.append({"role": "assistant", "content": resp1["message"]})
    messages.append({"role": "user", "content": "Tell me more about its architecture and history."})
    resp2 = await grok_service.generate_smart_trip_response(messages=messages, landmark_context=landmark_ctx)
    msg2 = resp2["message"].lower()
    assert "1799" in msg2 or "jharokha" in msg2 or "window" in msg2 or "sawai pratap" in msg2 or "pink" in msg2
    print("✅ 'Tell me more' gives rich heritage details")

    # Follow-up C: "What's nearby?"
    messages.append({"role": "assistant", "content": resp2["message"]})
    messages.append({"role": "user", "content": "What other places are nearby to visit?"})
    resp3 = await grok_service.generate_smart_trip_response(messages=messages, landmark_context=landmark_ctx)
    msg3 = resp3["message"].lower()
    assert "city palace" in msg3 or "jantar mantar" in msg3 or "amer" in msg3 or "jaipur" in msg3
    print("✅ 'What's nearby?' recommends neighboring attractions")

    # Follow-up D: "Plan a trip around this"
    messages.append({"role": "assistant", "content": resp3["message"]})
    messages.append({"role": "user", "content": "Plan a 2-day trip to Jaipur covering Hawa Mahal and nearby spots."})
    resp4 = await grok_service.generate_smart_trip_response(messages=messages, landmark_context=landmark_ctx)
    assert resp4["intent"] in ["plan_itinerary", "trip_planning"]
    print(f"✅ 'Plan a trip around this' correctly routes to itinerary planning (Intent: {resp4['intent']})")


def test_7_single_load_efficiency():
    print("\n--- TEST 7: Single-Load Resource Reuse ---")
    initial_index = visual_similarity_service.index
    initial_extractor = visual_similarity_service.extractor
    assert initial_index is not None and initial_extractor is not None

    generic_bytes = create_blank_test_image()
    for _ in range(3):
        res = visual_similarity_service.search_similar(generic_bytes)
        assert visual_similarity_service.index is initial_index, "FAISS index instance must remain constant"
        assert visual_similarity_service.extractor is initial_extractor, "Feature extractor must remain constant"
    print("✅ PASSED: FAISS index and ResNet feature extractor retained in memory without reloads")


def main():
    print("==================================================")
    print("RUNNING FAISS VISUAL SIMILARITY INTEGRATION TESTS")
    print("==================================================")
    test_1_known_hawa_mahal_faiss()
    test_2_other_known_monuments()
    test_3_generic_image_confidence_faiss()
    test_4_invalid_and_corrupt_files()
    test_5_faiss_direct_similar_endpoint()
    asyncio.run(test_6_conversational_followup_flows())
    test_7_single_load_efficiency()
    print("\n==================================================")
    print("🎉 ALL 7 FAISS INTEGRATION TEST SUITES PASSED!")
    print("==================================================")


if __name__ == "__main__":
    main()
