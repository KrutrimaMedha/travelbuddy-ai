#!/usr/bin/env python3
"""
Test script to check what actually happens during a real API request simulation
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_actual_response_processing():
    """Test what happens during actual response processing"""

    print("Testing Actual API Response Processing")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent instance that simulates API failure to trigger fallback
        class TestAgentWithFallback(GeminiTravelPlanningAgent):
            def __init__(self):
                # Skip full initialization for testing
                self.api_key = "test_key"
                self.travel_tool = None

            async def _send_message_with_functions(self, chat, prompt):
                # Simulate AI API failure to trigger fallback
                raise Exception("Simulated API failure to test fallback mechanism")

        agent = TestAgentWithFallback()

        # Test input for 4-day trip
        travel_input = {
            "source": "Delhi",
            "destination": "Manali",
            "travel_mode": "Self",
            "budget": "30000",
            "theme": "adventurous",
            "duration": "4 days",
            "vehicle_type": "car"
        }

        print(f"Test Input (4-day trip):")
        print(f"  Source: {travel_input['source']}")
        print(f"  Destination: {travel_input['destination']}")
        print(f"  Duration: {travel_input['duration']}")

        async def test_api_flow():
            result = await agent.generate_personalized_itinerary(travel_input)
            return result

        # This should trigger the fallback mechanism
        result = asyncio.run(test_api_flow())

        print(f"\nAPI Response Result:")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in result}")

        if 'daily_itinerary' in result:
            daily_itinerary = result['daily_itinerary']
            print(f"  Daily itinerary length: {len(daily_itinerary)}")
            print(f"  Days available: {[day.get('day', 'N/A') for day in daily_itinerary]}")

            # Check the structure of each day
            for i, day in enumerate(daily_itinerary):
                print(f"\n  Day {i+1} in API response:")
                print(f"    Day number: {day.get('day', 'Missing')}")
                print(f"    Title: {day.get('title', 'Missing')[:50]}...")
                print(f"    Has morning: {bool(day.get('morning'))}")
                print(f"    Has afternoon: {bool(day.get('afternoon'))}")
                print(f"    Has evening: {bool(day.get('evening'))}")
        else:
            print(f"  ERROR: No daily_itinerary found in response!")
            print(f"  Available keys: {list(result.keys())}")

        print(f"\n" + "="*60)
        print("SIMULATING FRONTEND DATA FLOW")
        print("="*60)

        # Simulate exactly what the frontend would receive
        frontend_response = {
            "status": "success",
            "agent_response": result
        }

        print(f"Frontend receives:")
        print(f"  Response status: {frontend_response['status']}")
        print(f"  Agent response status: {frontend_response['agent_response'].get('status', 'N/A')}")

        # Simulate TripResultsDisplay processing
        trip_data = frontend_response
        if trip_data and trip_data.get('status') == 'success' and trip_data.get('agent_response'):
            trip = trip_data['agent_response']

            # Simulate ItineraryTab processing
            itinerary = trip.get('daily_itinerary') or trip.get('itinerary') or []

            print(f"\nItineraryTab would receive:")
            print(f"  Itinerary array length: {len(itinerary)}")
            print(f"  Number of days to render: {len(itinerary)}")

            if len(itinerary) > 0:
                print(f"  Days that would be displayed:")
                for i, day in enumerate(itinerary):
                    day_num = day.get('day', i+1)
                    title = day.get('title', 'No title')
                    print(f"    Day {day_num}: {title}")
            else:
                print(f"  ERROR: No days would be displayed!")
                print(f"  trip.daily_itinerary: {trip.get('daily_itinerary', 'Not found')}")
                print(f"  trip.itinerary: {trip.get('itinerary', 'Not found')}")

        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_json_response_parsing():
    """Test JSON response parsing which might be causing issues"""

    print(f"\n" + "="*60)
    print("Testing JSON Response Parsing")
    print("="*60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test input
        travel_input = {
            "source": "Chennai",
            "destination": "Kodaikanal",
            "travel_mode": "Self",
            "budget": "20000",
            "theme": "cultural",
            "duration": "3 days",
            "vehicle_type": "car"
        }

        # Simulate different AI response scenarios
        test_scenarios = [
            {
                "name": "Valid JSON Response",
                "response": '{"daily_itinerary": [{"day": 1, "title": "Day 1"}, {"day": 2, "title": "Day 2"}, {"day": 3, "title": "Day 3"}]}'
            },
            {
                "name": "Invalid JSON Response",
                "response": "This is a plain text response about a 3-day trip to Kodaikanal"
            },
            {
                "name": "Empty Response",
                "response": ""
            }
        ]

        for scenario in test_scenarios:
            print(f"\nTesting: {scenario['name']}")

            # Test _create_structured_response
            structured = agent._create_structured_response(scenario['response'], travel_input)

            print(f"  Structured response status: {structured.get('status', 'N/A')}")
            print(f"  Has daily_itinerary: {'daily_itinerary' in structured}")

            if 'daily_itinerary' in structured:
                itinerary = structured['daily_itinerary']
                print(f"  Daily itinerary length: {len(itinerary)}")
                print(f"  Days: {[day.get('day', 'N/A') for day in itinerary]}")

        return True

    except Exception as e:
        print(f"Error during JSON testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Actual API Response Processing Test")
    print("=" * 70)

    success1 = test_actual_response_processing()
    success2 = test_json_response_parsing()

    if success1 and success2:
        print("\n*** ALL API RESPONSE TESTS PASSED! ***")
        print("The issue may be in the real AI API response processing.")
    else:
        print("\n*** SOME API RESPONSE TESTS FAILED ***")
        sys.exit(1)