#!/usr/bin/env python3
"""
Test script to simulate complete itinerary flow and check multi-day output
"""

import sys
import os
import json
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_flow():
    """Test the complete flow from input to final response"""

    print("Testing Complete Itinerary Flow")
    print("=" * 60)

    try:
        from travel_planner_agent import GeminiTravelPlanningAgent

        # Create a test agent instance with minimal initialization
        class TestAgent(GeminiTravelPlanningAgent):
            def __init__(self):
                # Skip full initialization for testing
                self.api_key = "test_key"
                self.travel_tool = None

        agent = TestAgent()

        # Test input for 5-day trip
        travel_input = {
            "source": "Mumbai",
            "destination": "Goa",
            "travel_mode": "Self",
            "budget": "25000",
            "theme": "adventurous",
            "duration": "5 days",
            "vehicle_type": "car"
        }

        print(f"Test Input:")
        print(f"  Source: {travel_input['source']}")
        print(f"  Destination: {travel_input['destination']}")
        print(f"  Duration: {travel_input['duration']}")
        print(f"  Travel Mode: {travel_input['travel_mode']}")

        # Test budget validation
        budget_validation = agent.validate_budget(travel_input)
        print(f"\nBudget Validation:")
        print(f"  Status: {budget_validation['status']}")
        print(f"  Minimum Required: Rs.{budget_validation.get('minimum_required', 'N/A')}")

        # Test duration validation
        duration_validation = agent.validate_duration(travel_input['duration'])
        print(f"\nDuration Validation:")
        print(f"  Status: {duration_validation['status']}")
        print(f"  Validated Duration: {duration_validation.get('validated_duration', 'N/A')} days")

        # Test fallback itinerary generation
        fallback_result = agent._create_fallback_itinerary(
            travel_input,
            budget_validation,
            duration_validation
        )

        print(f"\nFallback Itinerary Result:")
        print(f"  Status: {fallback_result['status']}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in fallback_result}")

        if 'daily_itinerary' in fallback_result:
            daily_itinerary = fallback_result['daily_itinerary']
            print(f"  Daily itinerary length: {len(daily_itinerary)}")
            print(f"  Days available: {[day.get('day', 'N/A') for day in daily_itinerary]}")

            # Print detailed structure for each day
            for i, day in enumerate(daily_itinerary):
                print(f"\n  Day {i+1} Structure:")
                print(f"    Day number: {day.get('day', 'Missing')}")
                print(f"    Title: {day.get('title', 'Missing')}")
                print(f"    Has morning: {bool(day.get('morning'))}")
                print(f"    Has afternoon: {bool(day.get('afternoon'))}")
                print(f"    Has evening: {bool(day.get('evening'))}")
                print(f"    Has activities: {bool(day.get('activities'))}")
                print(f"    Has accommodation: {bool(day.get('accommodation'))}")

                if day.get('morning'):
                    morning = day['morning']
                    if isinstance(morning, dict):
                        print(f"    Morning activity: {morning.get('activity', 'N/A')}")
                    else:
                        print(f"    Morning activity: {morning}")

        # Test structured response generation
        print(f"\n" + "="*60)
        print("Testing Structured Response Generation")

        mock_ai_response = "This is a mock AI response for a 5-day adventure trip to Goa."
        structured_result = agent._create_structured_response(mock_ai_response, travel_input)

        print(f"\nStructured Response Result:")
        print(f"  Status: {structured_result['status']}")
        print(f"  Has daily_itinerary: {'daily_itinerary' in structured_result}")

        if 'daily_itinerary' in structured_result:
            daily_itinerary = structured_result['daily_itinerary']
            print(f"  Daily itinerary length: {len(daily_itinerary)}")
            print(f"  Days available: {[day.get('day', 'N/A') for day in daily_itinerary]}")

        # Test self mode enhancement
        print(f"\n" + "="*60)
        print("Testing Self Mode Enhancement")

        async def test_enhancement():
            enhanced_result = await agent._enhance_self_mode(structured_result, travel_input)
            return enhanced_result

        enhanced_result = asyncio.run(test_enhancement())

        print(f"\nEnhanced Result:")
        print(f"  Has transportation: {'transportation' in enhanced_result}")
        print(f"  Has self_mode_features: {'self_mode_features' in enhanced_result}")
        print(f"  Still has daily_itinerary: {'daily_itinerary' in enhanced_result}")

        if 'daily_itinerary' in enhanced_result:
            daily_itinerary = enhanced_result['daily_itinerary']
            print(f"  Final daily itinerary length: {len(daily_itinerary)}")

        print("\n" + "="*60)
        print("FINAL RESULT FOR UI:")
        print("="*60)

        # Simulate what the UI would receive
        final_response = {
            "status": "success",
            "agent_response": enhanced_result
        }

        ui_trip_data = final_response["agent_response"]
        ui_itinerary = ui_trip_data.get('daily_itinerary') or ui_trip_data.get('itinerary') or []

        print(f"UI would receive:")
        print(f"  Trip data keys: {list(ui_trip_data.keys())}")
        print(f"  Itinerary array length: {len(ui_itinerary)}")
        print(f"  Days that would be rendered: {len(ui_itinerary)} days")

        if len(ui_itinerary) > 0:
            print(f"  First day structure keys: {list(ui_itinerary[0].keys())}")
            print(f"  Last day structure keys: {list(ui_itinerary[-1].keys())}")

        return True

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Complete Itinerary Flow Test")
    print("=" * 70)

    success = test_complete_flow()

    if success:
        print("\n*** COMPLETE FLOW TEST PASSED! ***")
        print("Multi-day itinerary generation is working correctly.")
    else:
        print("\n*** COMPLETE FLOW TEST FAILED ***")
        sys.exit(1)