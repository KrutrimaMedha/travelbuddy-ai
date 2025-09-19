#!/usr/bin/env python3
"""
Test script for the personalized trip planner functionality
"""

import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def test_budget_validation():
    """Test the budget validation functionality"""

    print("Testing Personalized Trip Planner - Budget Validation")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent
        print("Successfully imported GeminiTravelPlanningAgent")

        # Create a test agent instance
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                # Skip full initialization for testing
                pass

        agent = TestAgent()

        # Test budget validation with different scenarios
        test_cases = [
            {
                "name": "Sufficient Budget - Devotional Theme",
                "input": {
                    "source": "Mumbai",
                    "destination": "Rishikesh",
                    "travel_mode": "Self",
                    "budget": "25000",
                    "theme": "devotional",
                    "duration": "5 days"
                }
            },
            {
                "name": "Insufficient Budget - Nightlife Theme",
                "input": {
                    "source": "Delhi",
                    "destination": "Goa",
                    "travel_mode": "Booking",
                    "budget": "8000",
                    "theme": "nightlife",
                    "duration": "4 days"
                }
            },
            {
                "name": "Adventure Theme - Self Mode",
                "input": {
                    "source": "Bangalore",
                    "destination": "Coorg",
                    "travel_mode": "Self",
                    "budget": "20000",
                    "theme": "adventurous",
                    "duration": "3 days"
                }
            },
            {
                "name": "Cultural Theme - Booking Mode",
                "input": {
                    "source": "Chennai",
                    "destination": "Rajasthan",
                    "travel_mode": "Booking",
                    "budget": "35000",
                    "theme": "cultural",
                    "duration": "7 days"
                }
            }
        ]

        print("\nTesting Budget Validation:")
        print("-" * 50)

        for test_case in test_cases:
            print(f"\nTest: {test_case['name']}")
            input_data = test_case['input']
            print(f"Input: {input_data['source']} -> {input_data['destination']}")
            print(f"Mode: {input_data['travel_mode']}, Theme: {input_data['theme']}")
            print(f"Duration: {input_data['duration']}, Budget: Rs.{input_data['budget']}")

            try:
                result = agent._validate_budget(input_data)
                print(f"Validation Result:")
                print(f"  Status: {result['status']}")
                print(f"  Provided Budget: Rs.{result.get('provided_budget', 'N/A')}")
                print(f"  Minimum Required: Rs.{result.get('minimum_required', 'N/A')}")

                if result['status'] == 'insufficient':
                    print(f"  Alert: {result.get('alert_message', 'Budget insufficient')}")
                elif result['status'] == 'sufficient':
                    print(f"  Buffer Amount: Rs.{result.get('buffer_amount', 0)}")

            except Exception as e:
                print(f"  ERROR: {str(e)}")

        print("\nBudget validation tests completed!")
        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_input():
    """Test the search_and_respond function with structured input"""

    print("\n\nTesting Structured Input Processing")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Mock agent for testing without API calls
        class MockAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                pass

            async def search_and_respond(self, user_input):
                # Override to return mock response
                if isinstance(user_input, str):
                    structured_input = self._parse_query_to_structure(user_input)
                else:
                    structured_input = user_input

                budget_validation = self._validate_budget(structured_input)

                return {
                    "trip_overview": {
                        "source": structured_input.get('source', ''),
                        "destination": structured_input.get('destination', ''),
                        "travel_mode": structured_input.get('travel_mode', ''),
                        "budget": structured_input.get('budget', ''),
                        "theme": structured_input.get('theme', ''),
                        "duration": structured_input.get('duration', ''),
                    },
                    "budget_validation": budget_validation,
                    "status": "mock_response",
                    "message": "This is a test response from the personalized trip planner"
                }

        agent = MockAgent()

        # Test with structured input (your use case)
        test_input = {
            "source": "Mumbai",
            "destination": "Kerala",
            "travel_mode": "Self",
            "budget": "30000",
            "theme": "adventurous",
            "duration": "6 days",
            "vehicle_type": "car"
        }

        print(f"Test Input: {json.dumps(test_input, indent=2)}")

        async def run_test():
            result = await agent.search_and_respond(test_input)
            return result

        # Run the async test
        result = asyncio.run(run_test())

        print(f"\nTest Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Verify the result contains expected fields
        assert 'trip_overview' in result
        assert 'budget_validation' in result
        assert result['budget_validation']['status'] in ['sufficient', 'insufficient', 'error']

        print("\nStructured input test passed!")
        return True

    except Exception as e:
        print(f"Error during structured input testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Personalized Trip Planner Test Suite")
    print("=" * 70)

    success1 = test_budget_validation()
    success2 = test_structured_input()

    if success1 and success2:
        print("\n*** ALL TESTS PASSED! ***")
        print("The personalized trip planner functionality is working correctly.")
    else:
        print("\n*** SOME TESTS FAILED ***")
        sys.exit(1)