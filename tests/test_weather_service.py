import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.weather_service import get_weather_summary
from unittest.mock import patch, Mock

class TestWeatherService(unittest.TestCase):
    @patch('app.services.weather_service.requests.get')
    @patch('os.getenv')
    def test_get_weather_summary_success(self, mock_getenv, mock_get):
        """Test successful weather API call"""
        mock_getenv.return_value = 'test-weather-key'
        
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

        summary = get_weather_summary("Paris", "France", "2025-07-20", "2025-07-21")
        expected = (
            "2025-07-20: high 85°F, low 70°F, Sunny (precip chance 10%)\n"
            "2025-07-21: high 80°F, low 65°F, Cloudy (precip chance 20%)"
        )
        self.assertEqual(summary, expected)

    @patch('app.services.weather_service.requests.get')
    @patch('os.getenv')
    def test_get_weather_summary_api_fail(self, mock_getenv, mock_get):
        """Test handling weather API failure"""
        mock_getenv.return_value = 'test-weather-key'
        fake_resp = Mock(status_code=500)
        mock_get.return_value = fake_resp
        
        result = get_weather_summary("City", "Region", "2025-01-01", "2025-01-02")
        self.assertEqual(result, "Weather data unavailable.")

    @patch('os.getenv')
    def test_get_weather_summary_missing_api_key(self, mock_getenv):
        """Test handling missing weather API key"""
        mock_getenv.return_value = None
        
        result = get_weather_summary("City", "Region", "2025-01-01", "2025-01-02")
        self.assertEqual(result, "Weather API key not configured.")

if __name__ == '__main__':
    unittest.main()
