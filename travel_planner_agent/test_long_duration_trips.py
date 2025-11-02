#!/usr/bin/env python3
"""
Test script specifically for long duration trips (15+ days)
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_long_duration_scenarios():
    """Test long duration trip scenarios"""

    print("Testing Long Duration Trip Scenarios (15+ days)")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test scenarios with long durations
        test_scenarios = [
            {
                "name": "15-day North India tour",
                "input": {
                    "source": "Delhi",
                    "destination": "Rajasthan",
                    "travel_mode": "Self",
                    "budget": "75000",
                    "theme": "cultural",
                    "duration": "15 days",
                    "vehicle_type": "car"
                },
                "expected_days": 15
            },
            {
                "name": "20-day South India pilgrimage",
                "input": {
                    "source": "Chennai",
                    "destination": "Kerala",
                    "travel_mode": "Booking",
                    "budget": "80000",
                    "theme": "devotional",
                    "duration": "20 days"
                },
                "expected_days": 20
            },
            {
                "name": "25-day adventure expedition",
                "input": {
                    "source": "Mumbai",
                    "destination": "Ladakh",
                    "travel_mode": "Self",
                    "budget": "100000",
                    "theme": "adventurous",
                    "duration": "25 days",
                    "vehicle_type": "suv"
                },
                "expected_days": 25
            },
            {
                "name": "30-day complete India tour",
                "input": {
                    "source": "Bangalore",
                    "destination": "Kashmir",
                    "travel_mode": "Booking",
                    "budget": "150000",
                    "theme": "cultural",
                    "duration": "30 days"
                },
                "expected_days": 30
            }
        ]

        print("Step 1: Testing Duration Validation for Long Trips")
        print("-" * 50)

        for scenario in test_scenarios:
            print(f"\nTesting: {scenario['name']}")
            travel_input = scenario['input']
            expected_days = scenario['expected_days']

            print(f"  Input duration: {travel_input['duration']}")

            # Test duration validation
            duration_validation = agent.validate_duration(travel_input['duration'])
            print(f"  Duration validation result: {duration_validation}")

            validated_days = duration_validation.get('validated_duration', 0)
            print(f"  Validated days: {validated_days}")

            if validated_days == expected_days:
                print(f"  PASS: Duration validation correct")
            else:
                print(f"  FAIL: Expected {expected_days}, got {validated_days}")

        print(f"\n" + "="*60)
        print("Step 2: Testing Fallback Itinerary Generation for Long Trips")
        print("-" * 50)

        for scenario in test_scenarios:
            print(f"\nTesting fallback for: {scenario['name']}")
            travel_input = scenario['input']
            expected_days = scenario['expected_days']

            # Get validations
            budget_validation = agent.validate_budget(travel_input)
            duration_validation = agent.validate_duration(travel_input['duration'])

            # Test fallback itinerary generation
            print(f"  Generating fallback itinerary...")
            fallback_result = agent._create_fallback_itinerary(
                travel_input,
                budget_validation,
                duration_validation
            )

            print(f"  Fallback status: {fallback_result.get('status', 'N/A')}")
            print(f"  Has daily_itinerary: {'daily_itinerary' in fallback_result}")

            if 'daily_itinerary' in fallback_result:
                daily_itinerary = fallback_result['daily_itinerary']
                actual_days = len(daily_itinerary)
                print(f"  Generated days: {actual_days}")

                if actual_days == expected_days:
                    print(f"  PASS: Correct number of days generated")

                    # Sample first few and last few days
                    print(f"  First 3 days: {[day.get('day', 'N/A') for day in daily_itinerary[:3]]}")
                    print(f"  Last 3 days: {[day.get('day', 'N/A') for day in daily_itinerary[-3:]]}")

                    # Check structure of first and last day
                    first_day = daily_itinerary[0]
                    last_day = daily_itinerary[-1]

                    print(f"  First day structure: day={first_day.get('day')}, title='{first_day.get('title', '')[:30]}...'")
                    print(f"  Last day structure: day={last_day.get('day')}, title='{last_day.get('title', '')[:30]}...'")
                else:
                    print(f"  FAIL: Expected {expected_days} days, got {actual_days}")
            else:
                print(f"  FAIL: No daily_itinerary found in fallback result")

        print(f"\n" + "="*60)
        print("Step 3: Testing Complete API Flow for Long Trips")
        print("-" * 50)

        # Test one long trip through the complete flow
        long_trip_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "50000",
            "theme": "adventurous",
            "duration": "18 days",
            "vehicle_type": "car"
        }

        print(f"Testing complete flow for 18-day trip:")
        print(f"  Source: {long_trip_input['source']}")
        print(f"  Destination: {long_trip_input['destination']}")
        print(f"  Duration: {long_trip_input['duration']}")

        # Test the complete flow that would happen in real usage
        async def test_complete_flow():
            try:
                # This will trigger fallback since we don't have real API
                result = await agent.generate_personalized_itinerary(long_trip_input)
                return result
            except Exception as e:
                print(f"  API error (expected): {str(e)}")
                # Manually create the fallback flow
                budget_validation = agent.validate_budget(long_trip_input)
                duration_validation = agent.validate_duration(long_trip_input['duration'])
                return agent._create_fallback_itinerary(long_trip_input, budget_validation, duration_validation)

        result = asyncio.run(test_complete_flow())

        print(f"  Complete flow result status: {result.get('status', 'N/A')}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in result}")

        if 'daily_itinerary' in result:
            daily_itinerary = result['daily_itinerary']
            print(f"  Final itinerary length: {len(daily_itinerary)}")
            print(f"  All day numbers: {[day.get('day', 'N/A') for day in daily_itinerary]}")

            # Simulate what frontend would receive
            print(f"\n  FRONTEND SIMULATION:")
            print(f"  tripData.agent_response keys: {list(result.keys())}")

            # Simulate TripResultsDisplay processing
            trip = result
            overview = trip.get('trip_overview', {})
            print(f"  trip_overview.duration: {overview.get('duration', 'N/A')}")

            # Simulate ItineraryTab processing
            itinerary = trip.get('daily_itinerary') or trip.get('itinerary') or []
            print(f"  UI itinerary length: {len(itinerary)}")
            print(f"  UI would display {len(itinerary)} days")

        return True

    except Exception as e:
        print(f"Error during long duration testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_duration_edge_cases():
    """Test edge cases in duration parsing"""

    print(f"\n" + "="*60)
    print("Testing Duration Parsing Edge Cases")
    print("="*60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test various duration formats
        duration_test_cases = [
            {"input": "15 days", "expected": 15},
            {"input": "20days", "expected": 20},
            {"input": "25 Days", "expected": 25},
            {"input": "30 DAYS", "expected": 30},
            {"input": "15", "expected": 15},
            {"input": "2 weeks", "expected": 2},  # This might not work correctly
            {"input": "1 month", "expected": 1},  # This might not work correctly
            {"input": "35 days", "expected": 35},
        ]

        for test_case in duration_test_cases:
            duration_input = test_case['input']
            expected = test_case['expected']

            print(f"\nTesting duration: '{duration_input}'")

            result = agent.validate_duration(duration_input)
            validated_days = result.get('validated_duration', 0)

            print(f"  Validation result: {result}")
            print(f"  Extracted days: {validated_days}")

            if validated_days == expected:
                print(f"  PASS: Correctly parsed {expected} days")
            else:
                print(f"  ISSUE: Expected {expected}, got {validated_days}")

        return True

    except Exception as e:
        print(f"Error during duration edge case testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Long Duration Trip Testing")
    print("=" * 70)

    success1 = test_long_duration_scenarios()
    success2 = test_duration_edge_cases()

    if success1 and success2:
        print("\n*** LONG DURATION TESTS COMPLETED ***")
        print("Check the output above for any specific issues with 15+ day trips.")
    else:
        print("\n*** LONG DURATION TESTS FAILED ***")
        sys.exit(1)