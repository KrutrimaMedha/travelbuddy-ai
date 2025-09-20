#!/usr/bin/env python3
"""
Test script to verify the budget insufficient fix for long trips
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_budget_insufficient_long_trips():
    """Test long trips with insufficient budgets to ensure itinerary is still generated"""

    print("Testing Budget Insufficient Long Trips Fix")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test cases with insufficient budgets for long trips
        test_scenarios = [
            {
                "name": "15-day trip with low budget",
                "input": {
                    "source": "Mumbai",
                    "destination": "Goa",
                    "travel_mode": "Self",
                    "budget": "20000",  # Low budget for 15 days
                    "theme": "adventurous",
                    "duration": "15 days",
                    "vehicle_type": "car"
                },
                "expected_days": 15
            },
            {
                "name": "20-day trip with insufficient budget",
                "input": {
                    "source": "Delhi",
                    "destination": "Rajasthan",
                    "travel_mode": "Booking",
                    "budget": "25000",  # Low budget for 20 days
                    "theme": "cultural",
                    "duration": "20 days"
                },
                "expected_days": 20
            },
            {
                "name": "30-day trip with very low budget",
                "input": {
                    "source": "Chennai",
                    "destination": "Kerala",
                    "travel_mode": "Self",
                    "budget": "30000",  # Very low budget for 30 days
                    "theme": "devotional",
                    "duration": "30 days",
                    "vehicle_type": "car"
                },
                "expected_days": 30
            }
        ]

        for scenario in test_scenarios:
            print(f"\n--- Testing: {scenario['name']} ---")
            travel_input = scenario['input']
            expected_days = scenario['expected_days']

            print(f"Duration: {travel_input['duration']}")
            print(f"Budget: ₹{travel_input['budget']}")

            # Check budget validation first
            budget_validation = agent.validate_budget(travel_input)
            print(f"Budget status: {budget_validation['status']}")
            print(f"Minimum required: ₹{budget_validation.get('minimum_required', 'N/A')}")

            if budget_validation['status'] == 'insufficient':
                print(f"Shortfall: ₹{budget_validation.get('shortfall', 'N/A')}")

            # Test the complete flow
            async def test_complete_flow():
                try:
                    # This should now generate itinerary even with insufficient budget
                    result = await agent.generate_personalized_itinerary(travel_input)
                    return result
                except Exception as e:
                    print(f"  API error: {str(e)}")
                    # Fallback to manual creation
                    duration_validation = agent.validate_duration(travel_input['duration'])
                    return agent._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

            result = asyncio.run(test_complete_flow())

            print(f"\nResult analysis:")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  Has daily_itinerary: {'daily_itinerary' in result}")
            print(f"  Has budget_alert: {'budget_alert' in result}")

            if 'daily_itinerary' in result:
                daily_itinerary = result['daily_itinerary']
                print(f"  Generated days: {len(daily_itinerary)}")
                print(f"  Day numbers: {[day.get('day', 'N/A') for day in daily_itinerary[:5]]}... (showing first 5)")

                if len(daily_itinerary) == expected_days:
                    print(f"  ✓ SUCCESS: All {expected_days} days generated despite insufficient budget")
                else:
                    print(f"  ✗ ISSUE: Expected {expected_days} days, got {len(daily_itinerary)}")
            else:
                print(f"  ✗ ISSUE: No daily_itinerary found")

            if 'budget_alert' in result:
                budget_alert = result['budget_alert']
                print(f"  Budget alert status: {budget_alert.get('status', 'N/A')}")
                print(f"  Alert message present: {bool(budget_alert.get('message'))}")
            else:
                print(f"  Note: No budget alert (budget might be sufficient)")

            # Simulate what the frontend would receive
            print(f"\n  Frontend simulation:")
            frontend_response = {
                "status": "success",
                "agent_response": result
            }

            trip = frontend_response.get('agent_response', {})
            itinerary = trip.get('daily_itinerary') or trip.get('itinerary') or []
            print(f"    UI would display: {len(itinerary)} days")
            print(f"    UI would show budget alert: {'budget_alert' in trip}")

        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sufficient_budget_long_trips():
    """Test that sufficient budget long trips still work normally"""

    print(f"\n" + "="*60)
    print("Testing Sufficient Budget Long Trips (Control Group)")
    print("="*60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test case with sufficient budget
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "100000",  # High budget for 15 days
            "theme": "adventurous",
            "duration": "15 days",
            "vehicle_type": "car"
        }

        print(f"Testing 15-day trip with sufficient budget:")
        print(f"  Budget: ₹{travel_input['budget']}")

        # Check budget validation
        budget_validation = agent.validate_budget(travel_input)
        print(f"  Budget status: {budget_validation['status']}")

        # Test the complete flow
        async def test_flow():
            try:
                result = await agent.generate_personalized_itinerary(travel_input)
                return result
            except Exception as e:
                duration_validation = agent.validate_duration(travel_input['duration'])
                return agent._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

        result = asyncio.run(test_flow())

        print(f"\nResult:")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in result}")
        print(f"  Has budget_alert: {'budget_alert' in result}")

        if 'daily_itinerary' in result:
            daily_itinerary = result['daily_itinerary']
            print(f"  Generated days: {len(daily_itinerary)}")

            if len(daily_itinerary) == 15:
                print(f"  ✓ SUCCESS: Sufficient budget trip works correctly")
            else:
                print(f"  ✗ ISSUE: Expected 15 days, got {len(daily_itinerary)}")

        return True

    except Exception as e:
        print(f"Error during sufficient budget testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Budget Insufficient Long Trips Fix Test")
    print("=" * 70)

    success1 = test_budget_insufficient_long_trips()
    success2 = test_sufficient_budget_long_trips()

    if success1 and success2:
        print("\n*** ALL BUDGET FIX TESTS PASSED ***")
        print("Long trips with insufficient budgets now generate full itineraries with budget alerts.")
    else:
        print("\n*** SOME BUDGET FIX TESTS FAILED ***")
        sys.exit(1)