import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.shopping_service import get_overall_outfit_image, get_shopping_items
from unittest.mock import patch, Mock

class TestShoppingService(unittest.TestCase):
    @patch('app.services.shopping_service.GoogleSearch')
    @patch('os.getenv')
    def test_get_overall_outfit_image_success(self, mock_getenv, mock_google_search):
        """Test successful outfit image retrieval"""
        mock_getenv.return_value = 'test-serp-key'
        
        # Mock the GoogleSearch response
        mock_search_instance = Mock()
        mock_search_instance.get_dict.return_value = {
            "images_results": [
                {"thumbnail": "http://example.com/image1.jpg"},
                {"thumbnail": "http://example.com/image2.jpg"},
            ]
        }
        mock_google_search.return_value = mock_search_instance
        
        result = get_overall_outfit_image("summer dress", "female")
        self.assertEqual(result, "http://example.com/image1.jpg")

    @patch('os.getenv')
    def test_get_overall_outfit_image_missing_key(self, mock_getenv):
        """Test handling missing SERP API key"""
        mock_getenv.return_value = None
        
        result = get_overall_outfit_image("summer dress", "female")
        self.assertIsNone(result)

    @patch('app.services.shopping_service.GoogleSearch')
    @patch('os.getenv')
    def test_get_shopping_items_success(self, mock_getenv, mock_google_search):
        """Test successful shopping items retrieval"""
        mock_getenv.return_value = 'test-serp-key'
        
        # Mock the GoogleSearch response
        mock_search_instance = Mock()
        mock_search_instance.get_dict.return_value = {
            "shopping_results": [
                {
                    "title": "Summer Dress",
                    "price": "$29.99",
                    "link": "http://store.com/dress1",
                    "thumbnail": "http://store.com/thumb1.jpg",
                    "source": "Store A"
                },
                {
                    "title": "Casual Dress",
                    "price": "$39.99", 
                    "link": "http://store.com/dress2",
                    "thumbnail": "http://store.com/thumb2.jpg",
                    "source": "Store B"
                }
            ]
        }
        mock_google_search.return_value = mock_search_instance
        
        result = get_shopping_items("dress", "female", 2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Summer Dress")
        self.assertEqual(result[0]["price"], "$29.99")
        self.assertEqual(result[1]["title"], "Casual Dress")

    @patch('os.getenv')
    def test_get_shopping_items_missing_key(self, mock_getenv):
        """Test handling missing SERP API key for shopping"""
        mock_getenv.return_value = None
        
        result = get_shopping_items("dress", "female")
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
