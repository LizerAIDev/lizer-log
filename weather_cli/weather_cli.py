#!/usr/bin/env python3
"""Weather CLI tool — query real-time weather by city name.

Supports OpenWeatherMap API with 3 output formats: text, json, table.
API key must be set via WEATHER_API_KEY environment variable.

Usage:
    python weather_cli.py Beijing
    python weather_cli.py "New York" --format json
    python weather_cli.py 北京 --format table
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

import requests


# Default timeout for API requests (seconds)
REQUEST_TIMEOUT: int = 10

# OpenWeatherMap API base URL
API_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"


class WeatherAPIError(Exception):
    """Raised when the weather API returns an error response."""

    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class WeatherClient:
    """Client for fetching weather data from OpenWeatherMap API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = API_BASE_URL,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        """Initialize the weather client.

        Args:
            api_key: OpenWeatherMap API key. Defaults to WEATHER_API_KEY env var.
            base_url: API base URL. Defaults to OpenWeatherMap endpoint.
            timeout: Request timeout in seconds.

        Raises:
            WeatherAPIError: If no API key is provided.
        """
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY", "")
        if not self.api_key:
            raise WeatherAPIError(
                "No API key provided. Set WEATHER_API_KEY environment variable."
            )
        self.base_url = base_url
        self.timeout = timeout

    def fetch_weather(self, city: str) -> Dict[str, Any]:
        """Fetch current weather for a given city.

        Args:
            city: City name (supports Chinese and English names).

        Returns:
            Parsed JSON response from the API.

        Raises:
            WeatherAPIError: On network errors, API errors, or city not found.
        """
        params: Dict[str, str] = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise WeatherAPIError(f"Request timed out after {self.timeout}s.") from e
        except requests.exceptions.ConnectionError as e:
            raise WeatherAPIError(
                "Failed to connect to the weather service. Check your network."
            ) from e
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {e}") from e

        if response.status_code == 401:
            raise WeatherAPIError(
                "Invalid API key. Check your WEATHER_API_KEY.", status_code=401
            )
        if response.status_code == 404:
            raise WeatherAPIError(
                f"City '{city}' not found. Check the spelling.", status_code=404
            )
        if response.status_code != 200:
            raise WeatherAPIError(
                f"API error (HTTP {response.status_code}): {response.text.strip()}",
                status_code=response.status_code,
            )

        return response.json()

    def parse_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize weather fields from API response.

        Args:
            data: Raw API response dictionary.

        Returns:
            Normalized weather data dictionary with keys:
                city, country, temperature, feels_like, humidity,
                wind_speed, description, icon, timestamp.
        """
        main: Dict[str, Any] = data.get("main", {})
        wind: Dict[str, Any] = data.get("wind", {})
        weather_list: list = data.get("weather", [])
        weather: Dict[str, Any] = weather_list[0] if weather_list else {}

        return {
            "city": data.get("name", "Unknown"),
            "country": data.get("sys", {}).get("country", "N/A"),
            "temperature": main.get("temp", 0.0),
            "feels_like": main.get("feels_like", 0.0),
            "humidity": main.get("humidity", 0),
            "pressure": main.get("pressure", 0),
            "wind_speed": wind.get("speed", 0.0),
            "description": weather.get("description", "N/A"),
            "icon": weather.get("icon", ""),
            "timestamp": data.get("dt", 0),
        }


def format_text(weather: Dict[str, Any]) -> str:
    """Format weather data as human-readable text.

    Args:
        weather: Normalized weather data dictionary.

    Returns:
        Formatted text string.
    """
    lines = [
        "=" * 40,
        f"  Weather Report: {weather['city']}, {weather['country']}",
        "=" * 40,
        f"  Temperature:   {weather['temperature']:.1f}°C",
        f"  Feels Like:    {weather['feels_like']:.1f}°C",
        f"  Humidity:      {weather['humidity']}%",
        f"  Pressure:      {weather['pressure']} hPa",
        f"  Wind Speed:    {weather['wind_speed']:.1f} m/s",
        f"  Condition:     {weather['description'].title()}",
        "=" * 40,
    ]
    return "\n".join(lines)


def format_json(weather: Dict[str, Any]) -> str:
    """Format weather data as JSON string.

    Args:
        weather: Normalized weather data dictionary.

    Returns:
        JSON-formatted string with 2-space indent.
    """
    return json.dumps(weather, indent=2, ensure_ascii=False)


def format_table(weather: Dict[str, Any]) -> str:
    """Format weather data as an ASCII table.

    Args:
        weather: Normalized weather data dictionary.

    Returns:
        ASCII table string.
    """
    headers = ["Field", "Value"]
    rows = [
        ("City", f"{weather['city']}, {weather['country']}"),
        ("Temperature", f"{weather['temperature']:.1f}°C"),
        ("Feels Like", f"{weather['feels_like']:.1f}°C"),
        ("Humidity", f"{weather['humidity']}%"),
        ("Pressure", f"{weather['pressure']} hPa"),
        ("Wind Speed", f"{weather['wind_speed']:.1f} m/s"),
        ("Condition", weather["description"].title()),
    ]

    # Calculate column widths
    col1_width = max(len(h) for h in headers)
    col2_width = max(len(str(v)) for _, v in rows)
    col1_width = max(col1_width, len("Field"))
    col2_width = max(col2_width, len("Value"))

    sep = "+" + "-" * (col1_width + 2) + "+" + "-" * (col2_width + 2) + "+"

    def make_row(left: str, right: str) -> str:
        return f"| {left:<{col1_width}} | {right:<{col2_width}} |"

    lines = [
        sep,
        make_row(headers[0], headers[1]),
        sep,
    ]
    for key, value in rows:
        lines.append(make_row(key, value))
    lines.append(sep)

    return "\n".join(lines)


# Mapping of format names to formatter functions
FORMATTERS: Dict[str, Any] = {
    "text": format_text,
    "json": format_json,
    "table": format_table,
}


def main(argv: Optional[list] = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="Query real-time weather by city name.",
        epilog="Example: python weather_cli.py Beijing --format json",
    )
    parser.add_argument(
        "city",
        type=str,
        help="City name (supports Chinese and English)",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=list(FORMATTERS.keys()),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenWeatherMap API key (overrides WEATHER_API_KEY env var)",
    )

    args = parser.parse_args(argv)

    try:
        client = WeatherClient(api_key=args.api_key)
        raw_data = client.fetch_weather(args.city)
        weather = client.parse_weather(raw_data)
        formatter = FORMATTERS[args.format]
        print(formatter(weather))
        return 0
    except WeatherAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
