#!/usr/bin/env python3
"""
Test that simulates exactly what the real UI experiences
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_ui_simulation():
    """Simulate exactly what happens when the UI makes a real request"""

    print("Simulating Real UI Request Experience")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create the agent exactly as it would be in real usage
        class RealUITestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"  # This will trigger fallback behavior
                self.travel_tool = None

            async def _send_message_with_functions(self, chat, prompt):
                # Simulate various AI response scenarios that might cause the issue

                # Scenario 1: AI returns incomplete JSON with only 1 day
                incomplete_response_text = '''
                {
                    "trip_overview": {
                        "source": "Mumbai",
                        "destination": "Goa",
                        "duration": "15 days"
                    },
                    "daily_itinerary": [
                        {
                            "day": 1,
                            "title": "Arrival Day",
                            "morning": {"activity": "Arrive in Goa"},
                            "afternoon": {"activity": "Check into hotel"},
                            "evening": {"activity": "Beach walk"}
                        }
                    ]
                }
                '''

                # Create a mock response object
                class MockResponse:
                    def __init__(self, text):
                        self.text = text

                return MockResponse(incomplete_response_text)

        agent = RealUITestAgent()

        # Test with a 15-day trip request
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "75000",  # Sufficient budget
            "theme": "adventurous",
            "duration": "15 days",
            "vehicle_type": "car"
        }

        print(f"Testing real UI simulation:")
        print(f"  Duration: {travel_input['duration']}")
        print(f"  Budget: Rs.{travel_input['budget']}")

        async def simulate_real_request():
            result = await agent.generate_personalized_itinerary(travel_input)
            return result

        # This should trigger our validation and fallback mechanisms
        result = asyncio.run(simulate_real_request())

        print(f"\nResult Analysis (what UI would receive):")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Keys: {list(result.keys())}")

        # Check if daily_itinerary exists and has correct length
        daily_itinerary = result.get('daily_itinerary', [])
        print(f"  Daily itinerary length: {len(daily_itinerary)}")

        if len(daily_itinerary) == 15:
            print(f"  SUCCESS: All 15 days present")
        elif len(daily_itinerary) == 1:
            print(f"  ISSUE REPRODUCED: Only 1 day present (this is the bug!)")
        else:
            print(f"  UNEXPECTED: {len(daily_itinerary)} days present")

        if daily_itinerary:
            day_numbers = [day.get('day', 'N/A') for day in daily_itinerary]
            print(f"  Day numbers: {day_numbers}")

        # Simulate frontend processing
        print(f"\nFrontend Processing Simulation:")

        # This is exactly what TripResultsDisplay does
        frontend_trip_data = {
            "status": "success",
            "agent_response": result
        }

        # This is what gets passed to ItineraryTab
        trip = frontend_trip_data["agent_response"]
        ui_itinerary = trip.get('daily_itinerary') or trip.get('itinerary') or []

        print(f"  trip keys: {list(trip.keys())}")
        print(f"  UI itinerary length: {len(ui_itinerary)}")
        print(f"  UI would display: {len(ui_itinerary)} day cards")

        if len(ui_itinerary) == 15:
            print(f"  FRONTEND SUCCESS: UI will show all 15 days")
            return True
        else:
            print(f"  FRONTEND ISSUE: UI will only show {len(ui_itinerary)} days")
            return False

    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_different_ai_response_scenarios():
    """Test different AI response scenarios that might cause the issue"""

    print(f"\n" + "="*60)
    print("Testing Different AI Response Scenarios")
    print("="*60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class ScenarioTestAgent(GeminiTravelPlanningAgent):
            def __init__(self, scenario_response):
                self.api_key = "test_key"
                self.travel_tool = None
                self.scenario_response = scenario_response

            async def _send_message_with_functions(self, chat, prompt):
                class MockResponse:
                    def __init__(self, text):
                        self.text = text
                return MockResponse(self.scenario_response)

        travel_input = {
            "source": "Delhi",
            "destination": "Manali",
            "travel_mode": "Self",
            "budget": "60000",
            "theme": "adventurous",
            "duration": "12 days",
            "vehicle_type": "car"
        }

        scenarios = [
            {
                "name": "Empty JSON response",
                "response": "{}"
            },
            {
                "name": "JSON with empty daily_itinerary",
                "response": '{"daily_itinerary": []}'
            },
            {
                "name": "JSON with only 1 day",
                "response": '{"daily_itinerary": [{"day": 1, "title": "Day 1"}]}'
            },
            {
                "name": "Non-JSON response",
                "response": "Here is your travel plan for 12 days..."
            },
            {
                "name": "Malformed JSON",
                "response": '{"daily_itinerary": [{"day": 1'
            }
        ]

        for scenario in scenarios:
            print(f"\nTesting scenario: {scenario['name']}")

            agent = ScenarioTestAgent(scenario['response'])

            async def test_scenario():
                result = await agent.generate_personalized_itinerary(travel_input)
                return result

            result = asyncio.run(test_scenario())

            daily_itinerary = result.get('daily_itinerary', [])
            print(f"  Result: {len(daily_itinerary)} days generated")

            if len(daily_itinerary) == 12:
                print(f"  SUCCESS: Proper fallback worked")
            else:
                print(f"  ISSUE: Expected 12 days, got {len(daily_itinerary)}")

        return True

    except Exception as e:
        print(f"Error during scenario testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Real UI Simulation Test")
    print("=" * 70)

    success1 = test_real_ui_simulation()
    success2 = test_different_ai_response_scenarios()

    if success1 and success2:
        print("\n*** UI SIMULATION TESTS COMPLETED ***")
        print("Check output above to see if the UI issue was reproduced.")
    else:
        print("\n*** UI SIMULATION TESTS HAD ISSUES ***")
        sys.exit(1)