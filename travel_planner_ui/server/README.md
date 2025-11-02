# TravelBuddy FastAPI Gateway

This service powers the TravelBuddy UI by proxying requests to the `travel_planner_agent` package and exposing additional mock endpoints used by the frontend.

## 🚀 Quick Start

```bash
cd travel_planner_ui

# Install dependencies with uv (recommended)
uv pip install --no-cache-dir -r server/requirements.txt

# Export your Google Generative AI key (required for real trip planning)
export GEMINI_API_KEY=your_google_gen_ai_key

# Launch the API with reload for local development
uvicorn travel_planner_ui.server.main:app --host 0.0.0.0 --port 8000 --reload
```

The UI expects the gateway at `http://localhost:8000`. Adjust `VITE_API_URL` in the UI `.env` if you host it elsewhere.

## 🔑 Environment Variables

| Variable | Required | Description |
| --- | :---: | --- |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | ✅ | Google Generative AI key for the trip planner |
| `SERP_API_KEY` | ❌ | Optional SERP API token for richer search results |

## 🔌 Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/plan-trip` | Full AI-powered travel plan generation |
| `POST` | `/api/validate-budget` | Budget sufficiency analysis |
| `POST` | `/api/validate-duration` | Duration validation & recommendations |
| `POST` | `/api/mock-hotel-booking` | EaseMyTrip-style mock booking confirmation |
| `GET` | `/api/docs` | Swagger UI |
| `GET` | `/api/redoc` | ReDoc UI |

The generated OpenAPI specification is stored at `docs/api/openapi.json`.

## 🧪 Testing

The backend relies on `travel_planner_agent`, so you can reuse the agent test suite:

```bash
cd travel_planner_agent
uv run pytest
```

## 🛠️ Development Notes

- Mock booking payloads are retained in-memory (`mock_bookings`) for quick inspection.
- Logs are written to `travelbuddy_server.log` for easier debugging.
- When no API key is configured the server falls back to mock responses, keeping the UI functional for demos.
