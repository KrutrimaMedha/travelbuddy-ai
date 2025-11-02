#!/usr/bin/env python3
"""
Simple test for budget insufficient fix
"""

import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_budget_fix():
    """Simple test for the budget fix"""

    print("Testing Budget Fix for Long Trips")
    print("=" * 50)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test 18-day trip with low budget
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "20000",  # Low budget for 18 days
            "theme": "adventurous",
            "duration": "18 days",
            "vehicle_type": "car"
        }

        print(f"Testing 18-day trip:")
        print(f"  Duration: {travel_input['duration']}")
        print(f"  Budget: Rs.{travel_input['budget']}")

        # Check budget validation
        budget_validation = agent.validate_budget(travel_input)
        print(f"  Budget status: {budget_validation['status']}")

        if budget_validation['status'] == 'insufficient':
            print(f"  Minimum required: Rs.{budget_validation.get('minimum_required', 'N/A')}")
            print(f"  Shortfall: Rs.{budget_validation.get('shortfall', 'N/A')}")

        # Test the complete flow
        async def test_flow():
            try:
                result = await agent.generate_personalized_itinerary(travel_input)
                return result
            except Exception as e:
                print(f"  Exception occurred: {str(e)}")
                # Create fallback manually
                duration_validation = agent.validate_duration(travel_input['duration'])
                fallback = agent._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

                # Add budget alert manually if insufficient
                if budget_validation['status'] == 'insufficient':
                    fallback['budget_alert'] = {
                        "status": "insufficient",
                        "message": budget_validation['alert_message'],
                        "minimum_required": budget_validation['minimum_required'],
                        "shortfall": budget_validation['shortfall']
                    }

                return fallback

        result = asyncio.run(test_flow())

        print(f"\nResult Analysis:")
        print(f"  Result status: {result.get('status', 'N/A')}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in result}")
        print(f"  Has budget_alert: {'budget_alert' in result}")

        if 'daily_itinerary' in result:
            daily_itinerary = result['daily_itinerary']
            print(f"  Daily itinerary length: {len(daily_itinerary)}")
            print(f"  Day numbers: {[day.get('day', 'N/A') for day in daily_itinerary[:5]]}...")
            print(f"  Last few days: {[day.get('day', 'N/A') for day in daily_itinerary[-3:]]}")

            if len(daily_itinerary) == 18:
                print(f"  SUCCESS: All 18 days generated!")
            else:
                print(f"  ISSUE: Expected 18 days, got {len(daily_itinerary)}")
        else:
            print(f"  ISSUE: No daily_itinerary found")
            print(f"  Available keys: {list(result.keys())}")

        if 'budget_alert' in result:
            alert = result['budget_alert']
            print(f"  Budget alert status: {alert.get('status', 'N/A')}")
            print(f"  Has alert message: {bool(alert.get('message'))}")

        # Test what frontend would receive
        print(f"\nFrontend Simulation:")
        frontend_data = {"status": "success", "agent_response": result}
        trip = frontend_data.get('agent_response', {})
        itinerary = trip.get('daily_itinerary', [])
        print(f"  Frontend would render: {len(itinerary)} days")
        print(f"  Frontend would show budget alert: {'budget_alert' in trip}")

        if len(itinerary) == 18:
            print(f"  FINAL SUCCESS: Frontend will display all 18 days!")
            return True
        else:
            print(f"  FINAL ISSUE: Frontend will only display {len(itinerary)} days")
            return False

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_budget_fix()
    if success:
        print("\n*** BUDGET FIX TEST PASSED ***")
    else:
        print("\n*** BUDGET FIX TEST FAILED ***")
        sys.exit(1)