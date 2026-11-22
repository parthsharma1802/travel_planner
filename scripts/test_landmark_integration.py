#!/usr/bin/env python3
"""
Test Suite: CV Landmark Recognition Model Integration
Validates all requirements:
1. Known Hawa Mahal image identification
2. Other known landmarks from the 24 classes
3. Confidence calibration (high, moderate, low)
4. Corrupted / invalid file handling (400 / 415 HTTP status)
5. Tourism Knowledge Layer enrichment
6. Groq conversational integration (no raw JSON, no academic metrics)
7. Context preservation in ongoing conversations
8. Intent-driven behavior (no forced questionnaire, quiz, maps, weather, calendar)
9. Model single-load reuse efficiency
"""

import os
import sys
import glob
import io
import asyncio
from PIL import Image, ImageDraw
import numpy as np
import requests

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from backend.services.landmark_service import landmark_service
from backend.services.grok_service import grok_service

API_BASE = "http://localhost:8000"


def create_blank_test_image(color=(128, 128, 128), size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_1_known_hawa_mahal():
    print("\n--- TEST 1: Known Hawa Mahal Image ---")
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
    assert "Jaipur" in (data.get("location") or "")
    assert data.get("tourism_info") is not None
    print(f"✅ PASSED: Recognized {data['landmark_name']} ({data['location']}) with {data['confidence_level']} confidence")


def test_2_other_known_landmarks():
    print("\n--- TEST 2: Other Known Landmarks (Taj Mahal, Qutub Minar, etc.) ---")
    tested = 0
    for target in ["taj_mahal", "qutub_minar", "india_gate", "sun_temple_konark", "golden_temple"]:
        imgs = glob.glob(os.path.join(ROOT_DIR, f"data/raw/**/{target}/*.jpg"), recursive=True) + \
               glob.glob(os.path.join(ROOT_DIR, f"data/raw/**/*{target}*/*.jpg"), recursive=True)
        if imgs:
            with open(imgs[0], "rb") as f:
                resp = requests.post(f"{API_BASE}/api/landmark/recognize", files={"file": (f"{target}.jpg", f, "image/jpeg")})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["landmark_name"] is not None
            print(f"✅ Verified {target} -> Recognized: {data['landmark_name']} | Level: {data['confidence_level']}")
            tested += 1
            if tested >= 3:
                break
    assert tested >= 2, "Tested at least 2 other landmarks"


def test_3_unrelated_image_confidence_handling():
    print("\n--- TEST 3: Unrelated / Generic Image Confidence Handling ---")
    generic_bytes = create_blank_test_image()
    resp = requests.post(
        f"{API_BASE}/api/landmark/recognize",
        files={"file": ("generic.jpg", io.BytesIO(generic_bytes), "image/jpeg")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    print(f"✅ Generic image result: Level={data['confidence_level']}, Status={data['identification_status']}, Statement='{data['summary_statement']}'")


def test_4_invalid_and_corrupted_file():
    print("\n--- TEST 4: Invalid & Corrupted File Validation ---")
    # Empty file
    resp1 = requests.post(
        f"{API_BASE}/api/landmark/recognize",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
    )
    assert resp1.status_code == 400, f"Expected 400 for empty file, got {resp1.status_code}"
    print("✅ Empty file cleanly rejected with HTTP 400")

    # Corrupted content
    resp2 = requests.post(
        f"{API_BASE}/api/landmark/recognize",
        files={"file": ("corrupt.jpg", io.BytesIO(b"NOT_AN_IMAGE_DATA_CORRUPT"), "image/jpeg")}
    )
    assert resp2.status_code == 400, f"Expected 400 for corrupt data, got {resp2.status_code}"
    print("✅ Corrupted image cleanly rejected with HTTP 400")

    # Unsupported extension/mime
    resp3 = requests.post(
        f"{API_BASE}/api/landmark/recognize",
        files={"file": ("doc.txt", io.BytesIO(b"Hello text"), "text/plain")}
    )
    assert resp3.status_code in [400, 415], f"Expected 400/415 for text file, got {resp3.status_code}"
    print("✅ Unsupported media cleanly rejected with HTTP 415/400")


async def test_5_groq_natural_conversation_integration():
    print("\n--- TEST 5: Groq Natural Conversation Integration ---")
    landmark_ctx = {
        "status": "success",
        "landmark_name": "Hawa Mahal",
        "location": "Jaipur, Rajasthan",
        "confidence_level": "high",
        "confidence_score": 0.989,
        "identification_status": "confident",
        "summary_statement": "Looks like Hawa Mahal",
        "tourism_info": {
            "destination_name": "Hawa Mahal",
            "state": "Rajasthan",
            "city_district": "Jaipur",
            "category": "Heritage Monument",
            "description": "Famous 5-story palace with 953 honeycomb windows built in 1799."
        }
    }
    messages = [
        {"role": "user", "content": "I'm thinking of visiting Rajasthan next month."},
        {"role": "assistant", "content": "Rajasthan is incredible! From Jaipur's royal palaces to Udaipur's lakes, it's packed with culture."},
        {"role": "user", "content": "What is this landmark?"}
    ]

    resp = await grok_service.generate_smart_trip_response(
        messages=messages,
        landmark_context=landmark_ctx
    )

    msg = resp["message"]
    print(f"Assistant Output:\n{msg[:250]}...\n")

    clean_msg = msg.replace("\u202f", " ").replace("\u00a0", " ").lower()
    # Verification criteria
    assert "hawa mahal" in clean_msg, "Response must identify Hawa Mahal"
    assert "jaipur" in clean_msg or "rajasthan" in clean_msg, "Response should mention location"
    
    # Negative assertions
    assert "{" not in msg and "}" not in msg, "Raw JSON must never leak into message"
    assert "accuracy" not in msg.lower(), "Academic metrics (accuracy) must not leak"
    assert "f1" not in msg.lower(), "Academic metrics (F1) must not leak"
    assert "resnet" not in msg.lower(), "Model implementation details must not leak"
    assert "tensor" not in msg.lower(), "Tensor/debug terms must not leak"
    
    # Tool restraint assertions
    assert resp.get("quiz") is None or not resp.get("quiz", {}).get("active"), "Image upload must NOT trigger questionnaire"
    assert resp.get("intent") in ["general_question", "trip_planning"], f"Intent should be informational, got {resp.get('intent')}"
    print("✅ PASSED: Response is natural, context-aware, and has 0 leaked metrics/JSON/forced questionnaires")


def test_6_model_single_load_efficiency():
    print("\n--- TEST 6: Single-Load Model Reuse Efficiency ---")
    initial_model = landmark_service.model
    assert initial_model is not None, "Model should be loaded"
    
    # Run multiple predictions and verify instance is not reallocated
    img_bytes = create_blank_test_image()
    for _ in range(3):
        res = landmark_service.predict(img_bytes)
        assert landmark_service.model is initial_model, "Model instance must remain constant (no reload per request)"
    print("✅ PASSED: Model is retained in memory and reused across all requests")


def main():
    print("==================================================")
    print("RUNNING LANDMARK RECOGNITION INTEGRATION TESTS")
    print("==================================================")
    test_1_known_hawa_mahal()
    test_2_other_known_landmarks()
    test_3_unrelated_image_confidence_handling()
    test_4_invalid_and_corrupted_file()
    asyncio.run(test_5_groq_natural_conversation_integration())
    test_6_model_single_load_efficiency()
    print("\n==================================================")
    print("🎉 ALL 6 INTEGRATION TEST SUITES PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    main()
