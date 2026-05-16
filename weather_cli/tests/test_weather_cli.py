#!/usr/bin/env python3
"""Unit tests for weather_cli.py.

Tests cover: WeatherClient initialization, fetch errors, parsing,
output formatters, and CLI main entry point.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import weather_cli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_cli import (
    FORMATTERS,
    WeatherAPIError,
    WeatherClient,
    format_json,
    format_table,
    format_text,
    main,
)


# Sample API response fixture
SAMPLE_API_RESPONSE: dict = {
    "name": "Beijing",
    "sys": {"country": "CN"},
    "main": {
        "temp": 22.5,
        "feels_like": 21.0,
        "humidity": 45,
        "pressure": 1013,
    },
    "wind": {"speed": 3.6},
    "weather": [{"description": "scattered clouds", "icon": "03d"}],
    "dt": 1620000000,
}

SAMPLE_PARSED_WEATHER: dict = {
    "city": "Beijing",
    "country": "CN",
    "temperature": 22.5,
    "feels_like": 21.0,
    "humidity": 45,
    "pressure": 1013,
    "wind_speed": 3.6,
    "description": "scattered clouds",
    "icon": "03d",
    "timestamp": 1620000000,
}


class TestWeatherClientInit(unittest.TestCase):
    """Test WeatherClient initialization."""

    def test_init_with_env_var(self) -> None:
        """Client initializes successfully when WEATHER_API_KEY is set."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "test_key_123"}):
            client = WeatherClient()
            self.assertEqual(client.api_key, "test_key_123")

    def test_init_with_explicit_key(self) -> None:
        """Client uses explicit api_key over env var."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "env_key"}):
            client = WeatherClient(api_key="explicit_key")
            self.assertEqual(client.api_key, "explicit_key")

    def test_init_missing_api_key(self) -> None:
        """Client raises WeatherAPIError when no API key is available."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any existing key
            os.environ.pop("WEATHER_API_KEY", None)
            with self.assertRaises(WeatherAPIError) as ctx:
                WeatherClient()
            self.assertIn("No API key", str(ctx.exception))

    def test_init_custom_base_url(self) -> None:
        """Client accepts custom base_url."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient(base_url="https://custom.api/v1")
            self.assertEqual(client.base_url, "https://custom.api/v1")


class TestWeatherClientFetch(unittest.TestCase):
    """Test WeatherClient.fetch_weather method."""

    def test_fetch_success(self) -> None:
        """fetch_weather returns parsed JSON on HTTP 200."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_API_RESPONSE

        with patch("weather_cli.requests.get", return_value=mock_response) as mock_get:
            result = client.fetch_weather("Beijing")
            self.assertEqual(result, SAMPLE_API_RESPONSE)
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            self.assertEqual(call_kwargs["params"]["q"], "Beijing")

    def test_fetch_invalid_api_key(self) -> None:
        """fetch_weather raises WeatherAPIError on HTTP 401."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "bad_key"}):
            client = WeatherClient()

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("weather_cli.requests.get", return_value=mock_response):
            with self.assertRaises(WeatherAPIError) as ctx:
                client.fetch_weather("Beijing")
            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("Invalid API key", str(ctx.exception))

    def test_fetch_city_not_found(self) -> None:
        """fetch_weather raises WeatherAPIError on HTTP 404."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("weather_cli.requests.get", return_value=mock_response):
            with self.assertRaises(WeatherAPIError) as ctx:
                client.fetch_weather("NonExistentCity12345")
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("not found", str(ctx.exception))

    def test_fetch_timeout(self) -> None:
        """fetch_weather raises WeatherAPIError on request timeout."""
        import requests.exceptions as exc

        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()

        with patch(
            "weather_cli.requests.get", side_effect=exc.Timeout("timed out")
        ):
            with self.assertRaises(WeatherAPIError) as ctx:
                client.fetch_weather("Beijing")
            self.assertIn("timed out", str(ctx.exception))

    def test_fetch_connection_error(self) -> None:
        """fetch_weather raises WeatherAPIError on connection error."""
        import requests.exceptions as exc

        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()

        with patch(
            "weather_cli.requests.get",
            side_effect=exc.ConnectionError("connection refused"),
        ):
            with self.assertRaises(WeatherAPIError):
                client.fetch_weather("Beijing")


class TestWeatherClientParse(unittest.TestCase):
    """Test WeatherClient.parse_weather method."""

    def test_parse_full_response(self) -> None:
        """parse_weather extracts all expected fields."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()
            result = client.parse_weather(SAMPLE_API_RESPONSE)
            self.assertEqual(result["city"], "Beijing")
            self.assertEqual(result["country"], "CN")
            self.assertEqual(result["temperature"], 22.5)
            self.assertEqual(result["feels_like"], 21.0)
            self.assertEqual(result["humidity"], 45)
            self.assertEqual(result["pressure"], 1013)
            self.assertEqual(result["wind_speed"], 3.6)
            self.assertEqual(result["description"], "scattered clouds")

    def test_parse_minimal_response(self) -> None:
        """parse_weather handles response with missing optional fields."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            client = WeatherClient()
            minimal: dict = {"name": "TestCity"}
            result = client.parse_weather(minimal)
            self.assertEqual(result["city"], "TestCity")
            self.assertEqual(result["country"], "N/A")
            self.assertEqual(result["temperature"], 0.0)
            self.assertEqual(result["description"], "N/A")
            self.assertEqual(result["wind_speed"], 0.0)


class TestFormatters(unittest.TestCase):
    """Test output formatter functions."""

    def test_format_text_contains_city(self) -> None:
        """Text output includes city name."""
        output = format_text(SAMPLE_PARSED_WEATHER)
        self.assertIn("Beijing", output)
        self.assertIn("CN", output)

    def test_format_text_contains_temperature(self) -> None:
        """Text output includes temperature value."""
        output = format_text(SAMPLE_PARSED_WEATHER)
        self.assertIn("22.5", output)

    def test_format_json_valid(self) -> None:
        """JSON output is valid parseable JSON."""
        output = format_json(SAMPLE_PARSED_WEATHER)
        parsed = json.loads(output)
        self.assertEqual(parsed["city"], "Beijing")
        self.assertEqual(parsed["temperature"], 22.5)

    def test_format_json_unicode(self) -> None:
        """JSON output preserves Unicode characters."""
        weather = dict(SAMPLE_PARSED_WEATHER)
        weather["city"] = "北京"
        output = format_json(weather)
        self.assertIn("北京", output)

    def test_format_table_structure(self) -> None:
        """Table output has correct structure with separators."""
        output = format_table(SAMPLE_PARSED_WEATHER)
        lines = output.split("\n")
        # First and last lines should be separators
        self.assertTrue(lines[0].startswith("+"))
        self.assertTrue(lines[-1].startswith("+"))
        # Header row should contain Field and Value
        self.assertIn("Field", lines[1])
        self.assertIn("Value", lines[1])

    def test_format_table_contains_all_fields(self) -> None:
        """Table output includes all weather fields."""
        output = format_table(SAMPLE_PARSED_WEATHER)
        for key in ["City", "Temperature", "Humidity", "Wind Speed", "Condition"]:
            self.assertIn(key, output)


class TestFormattersMapping(unittest.TestCase):
    """Test FORMATTERS mapping is correct."""

    def test_formatters_has_three_keys(self) -> None:
        """FORMATTERS dict has exactly 3 format keys."""
        self.assertEqual(set(FORMATTERS.keys()), {"text", "json", "table"})

    def test_formatters_are_callable(self) -> None:
        """All formatter values are callable."""
        for name, func in FORMATTERS.items():
            self.assertTrue(callable(func), f"{name} formatter is not callable")


class TestMainCLI(unittest.TestCase):
    """Test the main() CLI entry point."""

    def test_main_missing_api_key(self) -> None:
        """main returns exit code 1 when no API key is set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("WEATHER_API_KEY", None)
            exit_code = main(["Beijing"])
            self.assertEqual(exit_code, 1)

    def test_main_invalid_format(self) -> None:
        """main rejects invalid --format value via argparse."""
        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            with self.assertRaises(SystemExit) as ctx:
                main(["Beijing", "--format", "xml"])
            self.assertNotEqual(ctx.exception.code, 0)

    @patch("weather_cli.WeatherClient")
    def test_main_success_text(self, mock_client_cls: MagicMock) -> None:
        """main prints formatted text and returns 0 on success."""
        mock_client = MagicMock()
        mock_client.fetch_weather.return_value = SAMPLE_API_RESPONSE
        mock_client.parse_weather.return_value = SAMPLE_PARSED_WEATHER
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            exit_code = main(["Beijing"])
            self.assertEqual(exit_code, 0)

    @patch("weather_cli.WeatherClient")
    def test_main_success_json(self, mock_client_cls: MagicMock) -> None:
        """main prints JSON format when --format json is passed."""
        mock_client = MagicMock()
        mock_client.fetch_weather.return_value = SAMPLE_API_RESPONSE
        mock_client.parse_weather.return_value = SAMPLE_PARSED_WEATHER
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            exit_code = main(["Beijing", "--format", "json"])
            self.assertEqual(exit_code, 0)

    @patch("weather_cli.WeatherClient")
    def test_main_city_not_found(self, mock_client_cls: MagicMock) -> None:
        """main returns exit code 1 when city is not found."""
        mock_client = MagicMock()
        mock_client.fetch_weather.side_effect = WeatherAPIError(
            "City 'FakeCity' not found.", status_code=404
        )
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"WEATHER_API_KEY": "k"}):
            exit_code = main(["FakeCity"])
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
