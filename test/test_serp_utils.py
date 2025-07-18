# tests/test_serp_utils.py
import unittest
from serp_utils import get_image_urls
from unittest.mock import patch

# fake GoogleSearch for testing
class FakeSearch:
    def __init__(self, params):
        self.params = params
    def get_dict(self):
        return {
            "images_results": [
                {"thumbnail": "thumb1"},
                {"original": "orig2"},
                {"thumbnail": None, "original": None},
            ]
        }

class TestSerpUtils(unittest.TestCase):
    @patch('serp_utils.GoogleSearch', new=FakeSearch)
    @patch('os.getenv', return_value='TEST_KEY')
    def test_get_image_urls_success(self, _mock_getenv):
        urls = get_image_urls("test query", num_results=2)
        # Should pick thumbnail then original, and stop at 2 results
        self.assertEqual(urls, ['thumb1', 'orig2'])

    @patch('os.getenv', return_value=None)
    def test_get_image_urls_missing_key(self, _mock_getenv):
        with self.assertRaises(EnvironmentError):
            get_image_urls("anything")
