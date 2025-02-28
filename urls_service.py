# urls_service.py
from constants import BASE_URL
from Singleton import Singleton

@Singleton
class UrlService:

    def __init__(self):
        pass  # No need for initialization here

    def get_track_request(self, track):
        return f"{BASE_URL}tracks/{track}/challenges?"

    def get_submissions_request(self, chal_slug):
        return f"{BASE_URL}challenges/{chal_slug}/submissions?"

    def get_particular_submission(self, chal_slug, sub_id):
        return f"{BASE_URL}challenges/{chal_slug}/submissions/{sub_id}"
