import aiohttp
from typing import Dict, Any, Optional


class WeatherTool:
    """
    Async weather client using Open-Meteo services (no API key required).

    Exposes high-level methods that return normalized dicts with 'status' and data.
    - get_current_weather(location)
    - get_forecast(location, days=7)
    - get_air_quality(location)
    """

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    async def _geocode(self, location: str, *, language: str = "en") -> Optional[Dict[str, Any]]:
        params = {"name": location, "count": 1, "language": language, "format": "json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.GEOCODE_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            results = data.get("results") or []
            if not results:
                return None
            top = results[0]
            return {
                "name": top.get("name"),
                "latitude": top.get("latitude"),
                "longitude": top.get("longitude"),
                "country": top.get("country"),
                "timezone": top.get("timezone"),
            }
        except Exception:
            return None

    async def get_current_weather(self, location: str, *, units: str = "metric") -> Dict[str, Any]:
        """Get current weather for a location by name."""
        geocoded = await self._geocode(location)
        if not geocoded:
            return {"status": "error", "message": f"Location not found: {location}"}

        lat = geocoded["latitude"]
        lon = geocoded["longitude"]
        temp_unit = "fahrenheit" if units == "imperial" else "celsius"
        wind_unit = "mph" if units == "imperial" else "kmh"

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "wind_speed_10m",
                "wind_gusts_10m",
                "wind_direction_10m",
                "weather_code",
            ],
            "temperature_unit": temp_unit,
            "wind_speed_unit": wind_unit,
            "precipitation_unit": "mm",
            "timezone": geocoded.get("timezone") or "auto",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.FORECAST_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            return {
                "status": "success",
                "location": geocoded,
                "units": units,
                "current": data.get("current"),
            }
        except Exception as e:
            return {"status": "error", "message": f"Current weather fetch failed: {e}"}

    async def get_forecast(self, location: str, *, days: int = 7, units: str = "metric") -> Dict[str, Any]:
        """Get daily forecast for N days (1-16 typical)."""
        geocoded = await self._geocode(location)
        if not geocoded:
            return {"status": "error", "message": f"Location not found: {location}"}

        days = max(1, min(int(days or 7), 16))
        temp_unit = "fahrenheit" if units == "imperial" else "celsius"
        wind_unit = "mph" if units == "imperial" else "kmh"

        params = {
            "latitude": geocoded["latitude"],
            "longitude": geocoded["longitude"],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "precipitation_hours",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
            ],
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability"],
            "forecast_days": days,
            "temperature_unit": temp_unit,
            "wind_speed_unit": wind_unit,
            "precipitation_unit": "mm",
            "timezone": geocoded.get("timezone") or "auto",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.FORECAST_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            return {
                "status": "success",
                "location": geocoded,
                "units": units,
                "daily": data.get("daily"),
                "hourly": data.get("hourly"),
            }
        except Exception as e:
            return {"status": "error", "message": f"Forecast fetch failed: {e}"}

    async def get_air_quality(self, location: str) -> Dict[str, Any]:
        """Get air quality (AQI-like pollutants) for a location."""
        geocoded = await self._geocode(location)
        if not geocoded:
            return {"status": "error", "message": f"Location not found: {location}"}

        params = {
            "latitude": geocoded["latitude"],
            "longitude": geocoded["longitude"],
            "hourly": [
                "pm10",
                "pm2_5",
                "carbon_monoxide",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone",
                "uv_index",
                "uv_index_clear_sky",
            ],
            "timezone": geocoded.get("timezone") or "auto",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.AIR_QUALITY_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            return {
                "status": "success",
                "location": geocoded,
                "air_quality": data.get("hourly"),
            }
        except Exception as e:
            return {"status": "error", "message": f"Air quality fetch failed: {e}"}


# Convenience singleton instance
weather_client = WeatherTool()

__all__ = ["WeatherTool", "weather_client"]

