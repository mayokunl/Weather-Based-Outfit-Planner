import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.helpers import parse_daily_outfits

class TestHelpers(unittest.TestCase):
    def test_parse_daily_outfits_success(self):
        """Test parsing GPT response with proper daily outfit format"""
        gpt_response = """
        ### Day 1:
        Here's your outfit for day 1:
        - Top: Blue shirt
        - Bottom: Jeans
        **Search Query:** blue shirt, jeans, sneakers

        ### Day 2:
        Here's your outfit for day 2:
        - Top: White dress
        - Accessories: Hat
        **Search Query:** white dress, summer hat
        """
        
        result = parse_daily_outfits(gpt_response)
        expected = {
            "Day 1": "blue shirt, jeans, sneakers",
            "Day 2": "white dress, summer hat"
        }
        self.assertEqual(result, expected)

    def test_parse_daily_outfits_no_search_query(self):
        """Test parsing GPT response without search query"""
        gpt_response = """
        ### Day 1:
        Here's your outfit for day 1:
        - Top: Blue shirt
        - Bottom: Jeans
        No search query provided.
        """
        
        result = parse_daily_outfits(gpt_response)
        expected = {"Day 1": "default outfit"}
        self.assertEqual(result, expected)

    def test_parse_daily_outfits_empty_response(self):
        """Test parsing empty GPT response"""
        result = parse_daily_outfits("")
        self.assertEqual(result, {})

    def test_parse_daily_outfits_malformed(self):
        """Test parsing malformed GPT response"""
        gpt_response = "This is not properly formatted"
        result = parse_daily_outfits(gpt_response)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
