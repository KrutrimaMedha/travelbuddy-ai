# 🌍 Travel Planner - AI-Powered Personalized Travel Planning System

A comprehensive AI-powered travel planning system that creates personalized trip plans using Google Generative AI with function calling capabilities. Supports both Self (own vehicle) and Booking (public transport) travel modes with theme-based recommendations.

## ✨ Features

- 🤖 **AI-Powered Planning**: Uses Google Generative AI for intelligent trip planning
- 🔍 **Real-time Search**: Integrates with SERP API for current travel information
- 🎯 **Theme-based Personalization**: Adventure, Cultural, Devotional, Nightlife themes
- 💰 **Budget Validation**: Smart budget analysis and optimization
- 🚗 **Multi-modal Transport**: Self-drive and public transport options
- 🌤️ **Weather Integration**: Weather-appropriate activity recommendations
- 📱 **Structured Responses**: JSON outputs ready for UI integration
- ⚡ **Async Support**: Full async/await implementation

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Google Generative AI API key
- SERP API key (optional, for enhanced search)

### Installation with uv (Recommended)

1. **Install uv** (if not already installed):

   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip
   pip install uv
   ```

2. **Clone and setup the project**:

   ```bash
   git clone <repository-url>
   cd travel-planner

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Install development dependencies** (optional):
   ```bash
   uv pip install -e ".[dev]"
   ```

### Installation with pip

```bash
git clone <repository-url>
cd travel-planner
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Environment Setup

Create a `.env` file in the project root:

```env
# Required: Google Generative AI API Key
GEMINI_API_KEY=your_gemini_api_key_here
# OR
GOOGLE_API_KEY=your_google_api_key_here

# Optional: SERP API Key for enhanced search
SERP_API_KEY=your_serp_api_key_here
```

**Getting API Keys:**

- **Google Generative AI**: Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **SERP API**: Get your key from [SerpApi](https://serpapi.com/) (optional, provides enhanced search)

## 📖 Usage

### Basic Usage

```python
import asyncio
from travel_planner import GeminiTravelPlanningAgent

async def main():
    # Initialize the agent
    agent = GeminiTravelPlanningAgent()

    # String query
    result = await agent.search_and_respond(
        "Plan a 3-day adventure trip to Goa with ₹15000 budget from Mumbai using own car"
    )

    # Structured query
    trip_request = {
        "source": "Mumbai",
        "destination": "Goa",
        "travel_mode": "Self",
        "budget": "₹15000",
        "theme": "Adventure",
        "duration": "3 days"
    }
    result = await agent.search_and_respond(trip_request)

    print(result)

# Run the example
asyncio.run(main())
```

### Budget Validation

```python
from travel_planner import GeminiTravelPlanningAgent

agent = GeminiTravelPlanningAgent()

# Validate budget for a trip
budget_result = agent.validate_budget(
    source="Mumbai",
    destination="Goa",
    travel_mode="Self",
    duration="3 days",
    budget="₹15000"
)

print(f"Budget valid: {budget_result['valid']}")
print(f"Minimum required: ₹{budget_result['minimum_required']}")
```

### Import Patterns

```python
# Main classes (recommended)
from travel_planner import GeminiTravelPlanningAgent

# Specific modules (if needed)
from travel_planner.travel_planning_tool import TravelPlanningTool
from travel_planner.travel_planning_agent import GeminiTravelPlanningAgent

# Both classes together
from travel_planner import GeminiTravelPlanningAgent, TravelPlanningTool
```

## 🧪 Testing

### Run All Tests

```bash
# With uv
uv run pytest

# With pip
pytest
```

### Run Specific Test Categories

### Run Example Scripts

```bash
# Simple functionality test
uv run python examples/test_agent_simple.py

# Comprehensive demo
uv run python examples/demo_agent_output.py

# Full API test (requires valid API keys)
uv run python examples/test_agent_run.py
```

## 📁 Project Structure

```
travel_planner/
├── src/                          # Source code
│   └── travel_planner/          # Main package
│       ├── __init__.py          # Package exports
│       ├── travel_planning_agent.py  # Main AI agent
│       ├── travel_planning_tool.py   # Search and data tools
│       └── prompts.py           # AI prompts and templates
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── test_travel_planning_agent.py
│   ├── test_travel_planning_tool.py
│   ├── test_integration.py
│   └── test_*.py               # Additional tests
├── examples/                    # Example scripts
│   ├── test_agent_simple.py    # Basic functionality demo
│   ├── demo_agent_output.py    # Comprehensive demo
│   ├── enhanced_agent_example.py # Advanced example
│   └── *.py                    # Other examples
├── pyproject.toml              # Project configuration
├── README.md                   # This file
├── LICENSE                     # MIT License
└── test_setup.py              # Setup verification script
```

## 🎯 Supported Travel Themes

- **🏔️ Adventure**: Water sports, trekking, paragliding, outdoor activities
- **🏛️ Cultural**: Museums, heritage sites, festivals, art galleries
- **🙏 Devotional**: Temple visits, meditation, spiritual experiences
- **🌃 Nightlife**: Clubs, bars, entertainment venues, night markets

## 🚗 Travel Modes

- **Self Mode**: Own vehicle with fuel cost calculations and route planning
- **Booking Mode**: Public transport with booking integration and cost estimates

## 📊 Response Format

The agent returns structured JSON responses with:

```json
{
  "trip_overview": {
    "source": "Mumbai",
    "destination": "Goa",
    "travel_mode": "Self",
    "budget": "₹15000",
    "theme": "Adventure",
    "duration": "3 days"
  },
  "destinations": [...],
  "hotels": [...],
  "restaurants": [...],
  "transportation": {...},
  "budget_breakdown": {...},
  "daily_itinerary": [...],
  "weather_info": {...}
}
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd travel-planner

# Install with development dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Code Quality Tools

```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run black --check src/ tests/
uv run isort --check-only src/ tests/
uv run flake8 src/ tests/
uv run mypy src/
```

### Running Tests in Development

```bash
# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=travel_planner --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_travel_planning_agent.py -v

# Run tests matching pattern
uv run pytest -k "test_budget" -v
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've installed the package with `uv pip install -e .`
2. **API Key Issues**: Verify your `.env` file has the correct API keys
3. **Network Errors**: Check your internet connection for API calls
4. **Module Not Found**: Ensure you're in the correct directory and virtual environment is activated

### Debug Mode

Set environment variable for detailed logging:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export DEBUG=1
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- 📧 Email: support@travelplanner.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/travel-planner/issues)
- 📖 Documentation: [Full Documentation](https://travel-planner.readthedocs.io)

---

**Made with ❤️ by the Travel Planner Team**
