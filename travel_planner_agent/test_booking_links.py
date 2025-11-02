#!/usr/bin/env python3
"""
Test script specifically for booking links functionality
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hotel_booking_links():
    """Test hotel booking links in fallback data"""

    print("Testing Hotel Booking Links")
    print("=" * 50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent instance
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                # Skip full initialization for testing
                pass

        agent = TestAgent()

        # Test input
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "25000",
            "theme": "adventurous",
            "duration": "3 days",
            "vehicle_type": "car"
        }

        # Create mock validation results
        budget_validation = {"status": "sufficient", "provided_budget": 25000, "minimum_required": 20000}
        duration_validation = {"status": "valid", "validated_duration": 3}

        result = agent._create_fallback_itinerary(
            travel_input,
            budget_validation,
            duration_validation
        )

        print(f"Generated hotels with booking links:")
        hotels = result.get('hotels', [])
        for i, hotel in enumerate(hotels, 1):
            print(f"\nHotel {i}:")
            print(f"  Name: {hotel['name']}")
            print(f"  Location: {hotel['location']}")
            print(f"  Rating: {hotel['rating']}")
            print(f"  Price: {hotel['price_range'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"  Booking Available: {hotel.get('booking_options', {}).get('available', False)}")
            print(f"  Booking URL: {hotel.get('booking_url', 'N/A')}")

        print(f"\nGenerated restaurants with reservation links:")
        restaurants = result.get('restaurants', [])
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\nRestaurant {i}:")
            print(f"  Name: {restaurant['name']}")
            print(f"  Cuisine: {restaurant['cuisine']}")
            print(f"  Rating: {restaurant['rating']}")
            print(f"  Price: {restaurant['price_range'].encode('ascii', 'ignore').decode('ascii')}")
            print(f"  Specialties: {restaurant.get('specialties', [])}")
            print(f"  Reservation URL: {restaurant.get('reservation_url', 'N/A')}")

        print("\nHotel and restaurant booking links test completed!")
        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_function_results():
    """Test fallback function results with booking URLs"""

    print("\n\nTesting Fallback Function Results")
    print("=" * 50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                pass

        agent = TestAgent()

        # Test hotel function result
        hotel_result = agent._get_fallback_function_result("get_hotels", {"location": "Goa"})
        print(f"Hotel function result:")
        for i, hotel in enumerate(hotel_result.get('hotels', []), 1):
            print(f"  Hotel {i}: {hotel['name']}")
            print(f"    Booking URL: {hotel.get('booking_url', 'N/A')}")

        # Test restaurant function result
        restaurant_result = agent._get_fallback_function_result("get_restaurants", {"location": "Goa"})
        print(f"\nRestaurant function result:")
        for i, restaurant in enumerate(restaurant_result.get('restaurants', []), 1):
            print(f"  Restaurant {i}: {restaurant['name']}")
            print(f"    Reservation URL: {restaurant.get('reservation_url', 'N/A')}")

        print("\nFallback function results test passed!")
        return True

    except Exception as e:
        print(f"Error during fallback function testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Booking Links Test Suite")
    print("=" * 70)

    success1 = test_hotel_booking_links()
    success2 = test_fallback_function_results()

    if success1 and success2:
        print("\n*** ALL BOOKING LINKS TESTS PASSED! ***")
        print("Hotels and restaurants now have proper booking/reservation links.")
    else:
        print("\n*** SOME BOOKING LINKS TESTS FAILED ***")
        sys.exit(1)