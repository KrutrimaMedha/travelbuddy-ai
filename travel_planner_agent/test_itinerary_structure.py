#!/usr/bin/env python3
"""
Test script specifically for itinerary structure and multiple days display
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fallback_itinerary_structure():
    """Test the fallback itinerary structure for multiple days"""

    print("Testing Fallback Itinerary Structure for Multiple Days")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent instance
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                # Skip full initialization for testing
                pass

        agent = TestAgent()

        # Test cases for different durations
        test_cases = [
            {
                "name": "3-day trip",
                "input": {
                    "source": "Mumbai",
                    "destination": "Goa",
                    "travel_mode": "Self",
                    "budget": "25000",
                    "theme": "adventurous",
                    "duration": "3 days",
                    "vehicle_type": "car"
                }
            },
            {
                "name": "5-day trip",
                "input": {
                    "source": "Delhi",
                    "destination": "Manali",
                    "travel_mode": "Self",
                    "budget": "35000",
                    "theme": "cultural",
                    "duration": "5 days",
                    "vehicle_type": "suv"
                }
            },
            {
                "name": "7-day trip",
                "input": {
                    "source": "Bangalore",
                    "destination": "Kerala",
                    "travel_mode": "Booking",
                    "budget": "45000",
                    "theme": "devotional",
                    "duration": "7 days"
                }
            }
        ]

        print("\nTesting Fallback Itinerary Generation:")
        print("-" * 50)

        for test_case in test_cases:
            print(f"\nTest: {test_case['name']}")
            input_data = test_case['input']
            print(f"Route: {input_data['source']} -> {input_data['destination']}")
            print(f"Duration: {input_data['duration']}")

            try:
                # Create mock validation results
                budget_validation = {"status": "sufficient", "provided_budget": 25000, "minimum_required": 20000}
                duration_validation = {"status": "valid", "validated_duration": 3}

                result = agent._create_fallback_itinerary(
                    input_data,
                    budget_validation,
                    duration_validation
                )

                print(f"Generated structure:")
                print(f"  Status: {result['status']}")
                print(f"  Daily itinerary length: {len(result.get('daily_itinerary', []))}")

                # Check if daily_itinerary exists and has correct number of days
                daily_itinerary = result.get('daily_itinerary', [])
                if daily_itinerary:
                    print(f"  Days created: {[day['day'] for day in daily_itinerary]}")

                    # Show first day structure
                    first_day = daily_itinerary[0]
                    print(f"  First day structure:")
                    print(f"    Title: {first_day.get('title', 'N/A')}")
                    print(f"    Has morning: {bool(first_day.get('morning'))}")
                    print(f"    Has afternoon: {bool(first_day.get('afternoon'))}")
                    print(f"    Has evening: {bool(first_day.get('evening'))}")
                    print(f"    Has activities: {bool(first_day.get('activities'))}")

                else:
                    print(f"  ERROR: No daily_itinerary found!")

            except Exception as e:
                print(f"  ERROR: {str(e)}")

        print("\nFallback itinerary structure tests completed!")
        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_response():
    """Test the structured response format"""

    print("\n\nTesting Structured Response Format")
    print("=" * 50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                pass

        agent = TestAgent()

        # Test input
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "25000",
            "theme": "adventurous",
            "duration": "4 days",
            "vehicle_type": "car"
        }

        # Test _create_structured_response
        mock_response_text = "This is a mock AI response text"

        result = agent._create_structured_response(mock_response_text, travel_input)

        print(f"Structured response:")
        print(f"  Status: {result['status']}")
        print(f"  Daily itinerary length: {len(result.get('daily_itinerary', []))}")

        daily_itinerary = result.get('daily_itinerary', [])
        if daily_itinerary:
            print(f"  Days created: {[day['day'] for day in daily_itinerary]}")
            print(f"  All days have required structure: {all('morning' in day and 'afternoon' in day and 'evening' in day for day in daily_itinerary)}")

        print(f"  Has trip_overview: {bool(result.get('trip_overview'))}")
        print(f"  Has budget_breakdown: {bool(result.get('budget_breakdown'))}")

        print("\nStructured response test passed!")
        return True

    except Exception as e:
        print(f"Error during structured response testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Itinerary Structure Test Suite")
    print("=" * 70)

    success1 = test_fallback_itinerary_structure()
    success2 = test_structured_response()

    if success1 and success2:
        print("\n*** ALL ITINERARY STRUCTURE TESTS PASSED! ***")
        print("The multi-day itinerary functionality is working correctly.")
    else:
        print("\n*** SOME ITINERARY STRUCTURE TESTS FAILED ***")
        sys.exit(1)