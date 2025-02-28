# test_urls_service.py
import unittest
from urls_service import UrlService
from constants import BASE_URL  # Import BASE_URL for verification

class TestUrlService(unittest.TestCase):
    def setUp(self):
        """Setup method to create an instance before each test."""
        self.url_service = UrlService.instance()

    def test_get_track_request(self):
        track_name = "python"
        expected_url = f"{BASE_URL}tracks/python/challenges?"
        actual_url = self.url_service.get_track_request(track_name)
        self.assertEqual(actual_url, expected_url)

    def test_get_submissions_request(self):
        chal_slug = "python-lists"
        expected_url = f"{BASE_URL}challenges/python-lists/submissions?"
        actual_url = self.url_service.get_submissions_request(chal_slug)
        self.assertEqual(actual_url, expected_url)

    def test_get_particular_submission(self):
        chal_slug = "python-lists"
        sub_id = 98765
        expected_url = f"{BASE_URL}challenges/python-lists/submissions/98765"
        actual_url = self.url_service.get_particular_submission(chal_slug, sub_id)
        self.assertEqual(actual_url, expected_url)


if __name__ == '__main__':
    unittest.main()
