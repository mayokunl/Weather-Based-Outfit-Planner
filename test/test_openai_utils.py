# tests/test_openai_utils.py
import unittest
from genai_utils import build_prompt_from_session, get_recommendations, HARDCODED_RESPONSE

class TestOpenAIUtils(unittest.TestCase):
    def test_build_prompt_from_session_with_data(self):
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
        self.assertIn('Gender:   Female', prompt)
        self.assertIn('Activities: museum, dining', prompt)
        self.assertIn('2025-07-20: high 85°F', prompt)

    def test_build_prompt_from_session_empty(self):
        prompt = build_prompt_from_session({})
        self.assertIn('Location: N/A, N/A', prompt)
        self.assertIn('Activities: general travel', prompt)

    def test_get_recommendations_returns_hardcoded(self):
        # Since the OpenAI call is bypassed, we get the HARDCODED_RESPONSE
        out = get_recommendations("anything")
        self.assertEqual(out, HARDCODED_RESPONSE)
