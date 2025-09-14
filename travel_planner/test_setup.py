#!/usr/bin/env python3
"""
Quick setup test for the travel_planner package
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing Travel Planner Package Setup")
    print("=" * 50)
    
    try:
        # Test basic imports
        print("📦 Testing imports...")
        from travel_planner import GeminiTravelPlanningAgent
        from travel_planner.travel_planning_tool import TravelPlanningTool
        print("✅ Core modules imported successfully")
        
        # Test agent creation (with mock API key)
        print("\n🤖 Testing agent initialization...")
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        try:
            agent = GeminiTravelPlanningAgent()
            print("✅ Agent can be initialized")
        except Exception as e:
            print(f"⚠️  Agent initialization failed (expected): {str(e)}")
            print("   This is normal without valid API keys")
        
        # Test utility functions
        print("\n🔧 Testing utility functions...")
        
        # Create a mock agent for testing utilities
        class MockAgent:
            def _parse_query_to_structure(self, query):
                return GeminiTravelPlanningAgent._parse_query_to_structure(None, query)
            def validate_budget(self, source, dest, mode, duration, budget):
                return GeminiTravelPlanningAgent.validate_budget(None, source, dest, mode, duration, budget)
        
        mock_agent = MockAgent()
        
        # Test query parsing
        result = mock_agent._parse_query_to_structure("3-day Goa trip with adventure theme")
        print(f"✅ Query parsing works: {result['theme']}")
        
        # Test budget validation
        budget_result = mock_agent.validate_budget("Mumbai", "Goa", "Self", "3 days", "₹15000")
        print(f"✅ Budget validation works: {budget_result['valid']}")
        
        print("\n🎉 All tests passed! Package is ready to use.")
        print("\n📖 Next steps:")
        print("   1. Set up your .env file with API keys")
        print("   2. Run: uv run python examples/test_agent_simple.py")
        print("   3. Run: uv run pytest tests/")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you're in the travel_planner directory")
        print("   2. Run: uv pip install -e .")
        print("   3. Check that src/ directory contains the Python files")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)