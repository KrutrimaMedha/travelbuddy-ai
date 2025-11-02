#!/usr/bin/env python3
"""
Final test to verify the complete itinerary fix
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_comprehensive_itinerary_scenarios():
    """Test various itinerary scenarios to ensure all days are generated"""

    print("Testing Comprehensive Itinerary Scenarios")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test scenarios with different durations
        test_scenarios = [
            {
                "name": "2-day weekend trip",
                "input": {
                    "source": "Mumbai",
                    "destination": "Lonavala",
                    "travel_mode": "Self",
                    "budget": "15000",
                    "theme": "adventurous",
                    "duration": "2 days",
                    "vehicle_type": "car"
                },
                "expected_days": 2
            },
            {
                "name": "5-day vacation",
                "input": {
                    "source": "Delhi",
                    "destination": "Rajasthan",
                    "travel_mode": "Booking",
                    "budget": "40000",
                    "theme": "cultural",
                    "duration": "5 days"
                },
                "expected_days": 5
            },
            {
                "name": "7-day pilgrimage",
                "input": {
                    "source": "Chennai",
                    "destination": "Tirupati",
                    "travel_mode": "Self",
                    "budget": "25000",
                    "theme": "devotional",
                    "duration": "7 days",
                    "vehicle_type": "car"
                },
                "expected_days": 7
            },
            {
                "name": "10-day extended trip",
                "input": {
                    "source": "Bangalore",
                    "destination": "Kerala",
                    "travel_mode": "Booking",
                    "budget": "50000",
                    "theme": "cultural",
                    "duration": "10 days"
                },
                "expected_days": 10
            }
        ]

        all_passed = True

        for scenario in test_scenarios:
            print(f"\n--- Testing: {scenario['name']} ---")
            travel_input = scenario['input']
            expected_days = scenario['expected_days']

            print(f"Duration: {travel_input['duration']}")
            print(f"Expected days: {expected_days}")

            # Test duration validation
            duration_validation = agent.validate_duration(travel_input['duration'])
            validated_days = duration_validation.get('validated_duration', 3)

            print(f"Validated days: {validated_days}")

            # Test fallback itinerary generation
            budget_validation = agent.validate_budget(travel_input)
            fallback_result = agent._create_fallback_itinerary(
                travel_input,
                budget_validation,
                duration_validation
            )

            daily_itinerary = fallback_result.get('daily_itinerary', [])
            actual_days = len(daily_itinerary)

            print(f"Generated days: {actual_days}")
            print(f"Day numbers: {[day.get('day', 'N/A') for day in daily_itinerary]}")

            if actual_days == expected_days:
                print(f"PASS: Correct number of days generated")
            else:
                print(f"FAIL: Expected {expected_days} days, got {actual_days}")
                all_passed = False

            # Test structured response generation
            structured_result = agent._create_structured_response("Mock AI response", travel_input)
            structured_itinerary = structured_result.get('daily_itinerary', [])
            structured_days = len(structured_itinerary)

            print(f"Structured response days: {structured_days}")

            if structured_days == expected_days:
                print(f"PASS: Structured response has correct days")
            else:
                print(f"FAIL: Structured expected {expected_days} days, got {structured_days}")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_response_validation():
    """Test the AI response validation that ensures all days are present"""

    print(f"\n" + "="*60)
    print("Testing AI Response Validation")
    print("="*60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "25000",
            "theme": "adventurous",
            "duration": "5 days",
            "vehicle_type": "car"
        }

        budget_validation = agent.validate_budget(travel_input)
        duration_validation = agent.validate_duration(travel_input['duration'])

        # Test scenarios with incomplete AI responses
        test_responses = [
            {
                "name": "Complete 5-day response",
                "response": '{"daily_itinerary": [{"day": 1}, {"day": 2}, {"day": 3}, {"day": 4}, {"day": 5}]}',
                "should_fallback": False
            },
            {
                "name": "Incomplete 2-day response (should trigger fallback)",
                "response": '{"daily_itinerary": [{"day": 1}, {"day": 2}]}',
                "should_fallback": True
            },
            {
                "name": "Empty itinerary (should trigger fallback)",
                "response": '{"daily_itinerary": []}',
                "should_fallback": True
            },
            {
                "name": "No itinerary field (should trigger fallback)",
                "response": '{"trip_overview": {"destination": "Goa"}}',
                "should_fallback": True
            }
        ]

        all_passed = True

        for test in test_responses:
            print(f"\nTesting: {test['name']}")

            # Simulate the _process_ai_response logic
            try:
                itinerary = json.loads(test['response'])

                # Apply the validation logic
                expected_days = duration_validation.get('validated_duration', 3)
                daily_itinerary = itinerary.get('daily_itinerary', [])

                if len(daily_itinerary) < expected_days:
                    print(f"  Validation triggered: AI generated {len(daily_itinerary)} days, expected {expected_days}")
                    # Would trigger structured response
                    final_result = agent._create_structured_response(test['response'], travel_input)
                    used_fallback = True
                else:
                    print(f"  Validation passed: AI generated {len(daily_itinerary)} days")
                    final_result = itinerary
                    used_fallback = False

                final_days = len(final_result.get('daily_itinerary', []))
                print(f"  Final result has {final_days} days")

                if test['should_fallback'] == used_fallback:
                    print(f"  PASS: Fallback behavior correct")
                else:
                    print(f"  FAIL: Expected fallback={test['should_fallback']}, got {used_fallback}")
                    all_passed = False

                if final_days == expected_days:
                    print(f"  PASS: Final result has correct number of days")
                else:
                    print(f"  FAIL: Final result has {final_days} days, expected {expected_days}")
                    all_passed = False

            except json.JSONDecodeError:
                print(f"  JSON decode error - would trigger structured response")
                final_result = agent._create_structured_response(test['response'], travel_input)
                final_days = len(final_result.get('daily_itinerary', []))
                print(f"  Final result has {final_days} days")

        return all_passed

    except Exception as e:
        print(f"Error during validation testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Final Itinerary Fix Validation Test")
    print("=" * 70)

    success1 = test_comprehensive_itinerary_scenarios()
    success2 = test_ai_response_validation()

    if success1 and success2:
        print("\n*** ALL FINAL TESTS PASSED! ***")
        print("Daily itinerary fix is working correctly for all scenarios.")
        print("All days should now be displayed in the UI.")
    else:
        print("\n*** SOME FINAL TESTS FAILED ***")
        sys.exit(1)