"""
Weather MCP server exposing weather tools using the Python MCP SDK.

Tools:
- get_current_weather(location: str, units: str = "metric")
- get_forecast(location: str, days: int = 7, units: str = "metric")
- get_air_quality(location: str)

Run: python -m weather_tool.server
"""

import asyncio
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from .weather_tool import weather_client


app = FastMCP("weather")


@app.tool()
async def get_current_weather(location: str, units: str = "metric") -> Dict[str, Any]:
    """Get current weather by location name. Units: metric|imperial."""
    return await weather_client.get_current_weather(location, units=units)


@app.tool()
async def get_forecast(location: str, days: int = 7, units: str = "metric") -> Dict[str, Any]:
    """Get daily forecast for N days (1..16). Units: metric|imperial."""
    return await weather_client.get_forecast(location, days=days, units=units)


@app.tool()
async def get_air_quality(location: str) -> Dict[str, Any]:
    """Get air quality metrics for a location."""
    return await weather_client.get_air_quality(location)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()

