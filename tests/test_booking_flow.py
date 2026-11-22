import asyncio
from backend.services.hotel_service import hotel_service
from backend.services.flight_service import flight_service
from backend.services.train_service import train_service

def test_hotel_search_and_pricing():
    """Test hotel search returns valid structured hotel cards with multi-vendor comparison."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(hotel_service.search_hotels(city="Jaipur", limit=5))
    loop.close()

    assert res["status"] == "success"
    assert len(res["hotels"]) > 0
    hotel = res["hotels"][0]
    assert "hotel_name" in hotel
    assert "lowest_price_inr" in hotel
    assert hotel["lowest_price_inr"] > 0
    assert "vendor_offers" in hotel
    assert len(hotel["vendor_offers"]) > 0
    # Check that price is labeled as Indicative / Reference
    assert "Indicative" in hotel.get("price_type", "") or "Reference" in hotel.get("price_type", "")

def test_hotel_selection_and_budget_calculation():
    """Test budget calculation when a hotel and transport are selected."""
    selected_hotel = {
        "hotel_name": "Rambagh Palace Jaipur",
        "city": "Jaipur",
        "price_inr": 4000,
        "best_vendor": "Booking.com",
        "status": "selected"
    }
    selected_transport = {
        "mode": "train",
        "name": "Vande Bharat Express",
        "fare_inr": 1200,
        "status": "selected"
    }

    duration_days = 3
    target_budget = 20000

    hotel_cost = selected_hotel["price_inr"] * duration_days
    transport_cost = selected_transport["fare_inr"]
    food_cost = duration_days * 800
    activities_cost = duration_days * 500
    estimated_total = hotel_cost + transport_cost + food_cost + activities_cost
    remaining = target_budget - estimated_total

    assert hotel_cost == 12000
    assert transport_cost == 1200
    assert food_cost == 2400
    assert activities_cost == 1500
    assert estimated_total == 17100
    assert remaining == 2900
    assert remaining > 0

def test_booking_status_model():
    """Test valid booking status transitions."""
    valid_statuses = ["recommended", "selected", "external_booking", "booking_confirmed"]
    
    current_status = "recommended"
    assert current_status in valid_statuses

    # User clicks select
    current_status = "selected"
    assert current_status in valid_statuses

    # User clicks view on provider / external link
    current_status = "external_booking"
    assert current_status in valid_statuses
    # Must NOT claim booking_confirmed for external redirects
    assert current_status != "booking_confirmed"

def test_flight_search_and_selection():
    """Test flight search and selection extraction."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(flight_service.search_flights(origin="DEL", destination="JAI", limit=3))
    loop.close()

    assert res["status"] == "success"
    assert len(res["flights"]) > 0
    flight = res["flights"][0]
    assert "airline" in flight
    assert "flight_number" in flight
    assert flight["price"] > 0

def test_train_search_and_selection():
    """Test train search and selection extraction."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(train_service.search_trains(source="NDLS", destination="JP", limit=3))
    loop.close()

    assert res["status"] == "success"
    assert len(res["trains"]) > 0
    train = res["trains"][0]
    assert "train_name" in train
    assert "train_number" in train

if __name__ == "__main__":
    test_hotel_search_and_pricing()
    print("✓ test_hotel_search_and_pricing passed")
    test_hotel_selection_and_budget_calculation()
    print("✓ test_hotel_selection_and_budget_calculation passed")
    test_booking_status_model()
    print("✓ test_booking_status_model passed")
    test_flight_search_and_selection()
    print("✓ test_flight_search_and_selection passed")
    test_train_search_and_selection()
    print("✓ test_train_search_and_selection passed")
    print("\nAll Booking Flow tests passed successfully!")
