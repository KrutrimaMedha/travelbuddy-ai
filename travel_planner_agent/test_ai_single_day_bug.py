#!/usr/bin/env python3
"""
Test to reproduce the specific bug where AI returns only 1 day for long trips
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ai_single_day_response():
    """Test what happens when AI returns only 1 day for a 15-day trip"""

    print("Testing AI Single Day Response Bug")
    print("=" * 50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test input for 15-day trip
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "75000",
            "theme": "adventurous",
            "duration": "15 days",
            "vehicle_type": "car"
        }

        # Simulate AI response with only 1 day (this might be what's happening in real API)
        ai_response_with_one_day = {
            "trip_overview": {
                "source": "Mumbai",
                "destination": "Goa",
                "travel_mode": "Self",
                "theme": "adventurous",
                "duration": "15 days",
                "budget": "75000"
            },
            "daily_itinerary": [
                {
                    "day": 1,
                    "title": "Arrival in Goa",
                    "morning": {"activity": "Depart from Mumbai", "location": "Mumbai", "duration": "4 hours", "cost": "Rs.2000"},
                    "afternoon": {"activity": "Arrive and check-in", "location": "Goa", "duration": "2 hours", "cost": "Rs.3000"},
                    "evening": {"activity": "Beach walk", "location": "Goa", "duration": "2 hours", "cost": "Rs.500"}
                }
            ],
            "hotels": [],
            "restaurants": [],
            "weather_info": {}
        }

        print(f"Simulating AI response with only 1 day for {travel_input['duration']} trip")

        # Get validations
        budget_validation = agent.validate_budget(travel_input)
        duration_validation = agent.validate_duration(travel_input['duration'])

        print(f"Expected days: {duration_validation.get('validated_duration', 'N/A')}")
        print(f"AI response days: {len(ai_response_with_one_day['daily_itinerary'])}")

        # Test the _process_ai_response logic directly
        print(f"\nTesting AI response processing...")

        # Simulate what happens in _process_ai_response
        response_text = json.dumps(ai_response_with_one_day)
        print(f"Response text starts with {{: {response_text.strip().startswith('{')}")

        try:
            # This is the exact logic from _process_ai_response
            itinerary = json.loads(response_text)
            print(f"JSON parsing successful")

            # Apply validation
            expected_days = duration_validation.get('validated_duration', 3)
            daily_itinerary = itinerary.get('daily_itinerary', [])

            print(f"Expected days: {expected_days}")
            print(f"AI generated days: {len(daily_itinerary)}")

            if len(daily_itinerary) < expected_days:
                print(f"VALIDATION TRIGGERED: Using structured response")
                itinerary = agent._create_structured_response(response_text, travel_input)

                # Check the structured response
                structured_daily_itinerary = itinerary.get('daily_itinerary', [])
                print(f"Structured response days: {len(structured_daily_itinerary)}")

                if len(structured_daily_itinerary) == expected_days:
                    print(f"SUCCESS: Structured response fixed the issue")
                else:
                    print(f"PROBLEM: Structured response still has wrong number of days")
            else:
                print(f"VALIDATION NOT TRIGGERED: AI response accepted as-is")
                print(f"This would result in only {len(daily_itinerary)} days being shown in UI!")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

        # Now test the complete flow
        print(f"\n" + "="*50)
        print("Testing Complete Flow with Single Day AI Response")

        # Simulate what would happen if we process this response
        final_itinerary = agent._create_structured_response(response_text, travel_input)

        # Add validation results
        final_itinerary['budget_validation'] = budget_validation
        final_itinerary['duration_validation'] = duration_validation

        print(f"Final result:")
        print(f"  Status: {final_itinerary.get('status', 'N/A')}")
        print(f"  Daily itinerary length: {len(final_itinerary.get('daily_itinerary', []))}")

        daily_itinerary = final_itinerary.get('daily_itinerary', [])
        if daily_itinerary:
            print(f"  Day numbers: {[day.get('day', 'N/A') for day in daily_itinerary]}")

        # Test what frontend would see
        print(f"\nFrontend would receive:")
        frontend_response = {"status": "success", "agent_response": final_itinerary}
        trip = frontend_response["agent_response"]
        ui_itinerary = trip.get('daily_itinerary') or trip.get('itinerary') or []
        print(f"  UI itinerary length: {len(ui_itinerary)}")

        if len(ui_itinerary) == 15:
            print(f"  SUCCESS: UI would show all 15 days")
            return True
        else:
            print(f"  BUG REPRODUCED: UI would only show {len(ui_itinerary)} days")
            return False

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_response_generation():
    """Test the _create_structured_response method specifically"""

    print(f"\n" + "="*50)
    print("Testing Structured Response Generation")
    print("="*50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        travel_input = {
            "source": "Delhi",
            "destination": "Manali",
            "travel_mode": "Self",
            "budget": "60000",
            "theme": "adventurous",
            "duration": "18 days",
            "vehicle_type": "car"
        }

        print(f"Testing structured response for {travel_input['duration']} trip")

        # Test the structured response method directly
        response_text = "Mock AI response text"
        structured = agent._create_structured_response(response_text, travel_input)

        print(f"Structured response:")
        print(f"  Status: {structured.get('status', 'N/A')}")
        print(f"  Keys: {list(structured.keys())}")

        daily_itinerary = structured.get('daily_itinerary', [])
        print(f"  Daily itinerary length: {len(daily_itinerary)}")

        if daily_itinerary:
            print(f"  Day numbers: {[day.get('day', 'N/A') for day in daily_itinerary]}")
            print(f"  Sample first day: {daily_itinerary[0].get('day', 'N/A')} - {daily_itinerary[0].get('title', 'No title')}")
            print(f"  Sample last day: {daily_itinerary[-1].get('day', 'N/A')} - {daily_itinerary[-1].get('title', 'No title')}")

        if len(daily_itinerary) == 18:
            print(f"  SUCCESS: Structured response generates all 18 days")
            return True
        else:
            print(f"  ISSUE: Structured response only generates {len(daily_itinerary)} days")
            return False

    except Exception as e:
        print(f"Error during structured response testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("AI Single Day Bug Test")
    print("=" * 70)

    success1 = test_ai_single_day_response()
    success2 = test_structured_response_generation()

    if success1 and success2:
        print("\n*** SINGLE DAY BUG TESTS PASSED ***")
        print("The validation and fallback mechanisms are working correctly.")
    else:
        print("\n*** SINGLE DAY BUG REPRODUCED ***")
        print("Found the issue causing only 1 day to be displayed.")
        sys.exit(1)