import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.openai_service import build_prompt_from_session, get_recommendations
from unittest.mock import patch, Mock

class TestOpenAIService(unittest.TestCase):
    def test_build_prompt_from_session_with_data(self):
        """Test building prompt with complete session data"""
        session = {
            'city': 'Paris',
            'region': 'France',
            'gender': 'Female',
            'age': '30',
            'activities': ['museum', 'dining'],
            'days': 3,
            'weather_summary': '2025-07-20: high 85°F, low 70°F, Sunny'
        }
        prompt = build_prompt_from_session(session)
        self.assertIn('Location: Paris, France', prompt)
        self.assertIn('Gender: Female', prompt)
        self.assertIn('Activities: museum, dining', prompt)
        self.assertIn('2025-07-20: high 85°F', prompt)

    def test_build_prompt_from_session_empty(self):
        """Test building prompt with empty session data"""
        prompt = build_prompt_from_session({})
        self.assertIn('Location: N/A, N/A', prompt)
        self.assertIn('Activities: general travel', prompt)
        self.assertIn('Duration: multi-day days', prompt)

    @patch('app.services.openai_service.OpenAI')
    @patch('os.getenv')
    def test_get_recommendations_success(self, mock_getenv, mock_openai):
        """Test successful OpenAI API call"""
        mock_getenv.return_value = 'test-api-key'
        
        # Mock the OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test outfit recommendation"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = get_recommendations("test prompt")
        self.assertEqual(result, "Test outfit recommendation")

    @patch('os.getenv')
    def test_get_recommendations_missing_api_key(self, mock_getenv):
        """Test handling missing API key"""
        mock_getenv.return_value = None
        
        result = get_recommendations("test prompt")
        self.assertEqual(result, "OpenAI API key not configured.")

if __name__ == '__main__':
    unittest.main()
