# Weather Tool (MCP)

A minimal Weather MCP tool that exposes current weather, forecast, and air quality as MCP tools. Internally uses Open‑Meteo (no API key required).

## Structure

```
weather_tool/
├── src/weather_tool/
│   ├── __init__.py
│   ├── weather_tool.py      # Async weather client (Open‑Meteo)
│   └── server.py            # MCP server exposing tools
└── pyproject.toml
```

## Setup

```bash
cd weather_tool
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Run MCP Server

```bash
# Either
python -m weather_tool.server
# Or
uv run python -m weather_tool.server
```

The server exposes the following tools:
- get_current_weather(location)
- get_forecast(location, days)
- get_air_quality(location)

## Notes
- Uses Open‑Meteo free APIs (no key required):
  - Geocoding: https://geocoding-api.open-meteo.com
  - Forecast: https://api.open-meteo.com
  - Air quality: https://air-quality-api.open-meteo.com
- Network access is required at runtime to fetch data.

## Example (Programmatic)

```python
import asyncio
from weather_tool.weather_tool import weather_client

async def main():
    print(await weather_client.get_current_weather("London"))
    print(await weather_client.get_forecast("San Francisco", days=5))
    print(await weather_client.get_air_quality("Delhi"))

asyncio.run(main())
```

---

MIT License
