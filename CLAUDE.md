# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a Python-based AI travel planning system with a two-level structure:
- **Root level**: Container project (`travelbuddy-ai`) with basic configuration
- **Main package**: `travel_planner_agent/` contains the complete, self-contained travel planning system

The actual development work happens in `travel_planner_agent/` directory, which has its own virtual environment, dependencies, and configuration.

## Working Directory

Always work from the `travel_planner_agent/` directory for development tasks:

```bash
cd travel_planner_agent
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment and install dependencies
cd travel_planner_agent
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=travel_planner --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_travel_planning_agent.py -v

# Run tests matching pattern
uv run pytest -k "test_budget" -v
```

### Code Quality
```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks together
uv run black --check src/ tests/ && uv run isort --check-only src/ tests/ && uv run flake8 src/ tests/ && uv run mypy src/
```

### Running Examples
```bash
# Simple functionality test
uv run python examples/test_agent_simple.py

# Comprehensive demo
uv run python examples/demo_agent_output.py

# Full API test (requires valid API keys)
uv run python examples/enhanced_agent_example.py
```

## Architecture Overview

### Core Components

1. **GeminiTravelPlanningAgent** (`travel_planning_agent.py`): Main AI agent that orchestrates travel planning using Google Generative AI with function calling
2. **TravelPlanningTool** (`travel_planning_tool.py`): Handles search operations, data fetching, and budget validation
3. **prompts.py**: Contains AI prompts and templates for different travel themes

### Key Features
- **Multi-modal Transport**: Supports both "Self" (own vehicle) and "Booking" (public transport) modes
- **Theme-based Planning**: Adventure, Cultural, Devotional, Nightlife themes
- **Budget Validation**: Smart cost analysis and optimization
- **Async Support**: Full async/await implementation throughout
- **Structured Output**: JSON responses designed for UI integration

### API Integration
- **Google Generative AI**: Primary AI engine for travel planning
- **SERP API**: Optional real-time search for enhanced travel information
- **Weather Integration**: Weather-appropriate activity recommendations

## Environment Variables

Required `.env` file in `travel_planner_agent/` directory:

```env
# Required: Google Generative AI API Key
GEMINI_API_KEY=your_gemini_api_key_here
# OR
GOOGLE_API_KEY=your_google_api_key_here

# Optional: SERP API Key for enhanced search
SERP_API_KEY=your_serp_api_key_here
```

## Import Patterns

```python
# Main classes (recommended)
from travel_planner import GeminiTravelPlanningAgent

# Specific modules (if needed)
from travel_planner.travel_planning_tool import TravelPlanningTool
from travel_planner.travel_planning_agent import GeminiTravelPlanningAgent

# Both classes together
from travel_planner import GeminiTravelPlanningAgent, TravelPlanningTool
```

## Development Workflow

1. Always work in the `travel_planner_agent/` directory
2. Ensure virtual environment is activated before running commands
3. Use `uv` package manager for dependency management
4. Run tests after making changes: `uv run pytest`
5. Run code quality checks before committing: `uv run black src/ tests/ && uv run flake8 src/ tests/`
6. Type checking is configured with mypy - run `uv run mypy src/` to validate types