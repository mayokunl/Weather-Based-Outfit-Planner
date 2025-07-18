# tests/test_weather_utils.py
import unittest
from weather_utils import get_weather_summary
from unittest.mock import patch, Mock

class TestWeatherUtils(unittest.TestCase):
    @patch('weather_utils.requests.get')
    def test_get_weather_summary_success(self, mock_get):
        fake_resp = Mock(status_code=200)
        fake_resp.json.return_value = {
            "days": [
                {"datetime": "2025-07-20", "tempmax": 85, "tempmin": 70,
                 "conditions": "Sunny", "precipprob": 10},
                {"datetime": "2025-07-21", "tempmax": 80, "tempmin": 65,
                 "conditions": "Cloudy", "precipprob": 20},
            ]
        }
        mock_get.return_value = fake_resp

        summary = get_weather_summary("City", "Region", "2025-07-20", "2025-07-21")
        expected = (
            "2025-07-20: high 85°F, low 70°F, Sunny (precip chance 10%)\n"
            "2025-07-21: high 80°F, low 65°F, Cloudy (precip chance 20%)"
        )
        self.assertEqual(summary, expected)

    @patch('weather_utils.requests.get')
    def test_get_weather_summary_api_fail(self, mock_get):
        fake_resp = Mock(status_code=500)
        mock_get.return_value = fake_resp
        self.assertEqual(
            get_weather_summary("X", "Y", "2025-01-01", "2025-01-02"),
            "Weather data unavailable."
        )
