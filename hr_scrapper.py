# hr_scrapper.py  (Option 1 - Keeping URL methods in HR_Scrapper)
import requests
from urls_service import UrlService  # Keep your UrlService, even if not used for now
from credentials import CSRF_TOKEN, COOKIE  # Keep your credentials
import json
import time
import os  # Import os for file handling
from util import get_file_extension  # Keep your utility functions
from models import get_code_result_model #keep your models
from constants import BASE_DIR, BASE_URL # Keep your contants


class HR_Scrapper:
    def __init__(self, base_delay=2):
        self.url_service = UrlService.instance()  # Keep, but not used for now
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Cookie": COOKIE,
            "x-csrf-token": CSRF_TOKEN,
            "accept": "application/json",
            "content-type": "application/json",
            "referer": "https://www.hackerrank.com/submissions/all"
        }
        self.base_delay = base_delay
        self.PREFIX = "__" # Your prefix

    def get_track(self, track):
        # --- Use the HR_Scrapper's own methods ---
        url = self.get_track_url(track)  # Call HR_Scrapper's method
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tracks = response.json()
            models = tracks['models']
            for i in models:
                chal_slug = i.get('slug')
                sub_domain = i.get('track').get('slug')
                if chal_slug is None:
                    raise Exception("Chal_slug:" + str(chal_slug))

                sub_domain_string = "Domain: " + sub_domain
                print(track + " " + sub_domain_string + chal_slug.rjust(70 - len(sub_domain_string)))

                sub_id = self.get_submissions(chal_slug)  # Call HR_Scrapper's get_submissions
                code = False
                if sub_id:
                    result = self.get_code(chal_slug, sub_id)  # Call HR_Scrapper's get_code
                    code = result['code']
                    lang = result['language']

                if code:
                    ext = get_file_extension(track, lang)
                    self.create_code_file(track, sub_domain, chal_slug, code, ext)
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {track}: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error for {track}: {e}")
            print(f"Response content: {response.text}")
        finally:
            time.sleep(self.base_delay)

    def get_submissions(self, chal_slug):
        url = self.get_submissions_url(chal_slug) # Call HR_Scrapper's method
        try:
            submissions = requests.get(url, headers=self.headers)
            submissions.raise_for_status()
            models = submissions.json()['models']
            if len(models) > 0:
                sub_id = models[0]['id']
                return sub_id
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request failed in get_submissions for {chal_slug}: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in get_submissions for {chal_slug}: {e}")
            print(f"Response content: {submissions.text}")
            return False

    def get_code(self, chal_slug, sub_id):
        url = self.get_particular_submission_url(chal_slug, sub_id) # Call HR_Scrapper's method
        try:
            code_res = requests.get(url, headers=self.headers)
            code_res.raise_for_status()
            model = code_res.json()['model']
            code = model['code']
            language = model['language']
            result = dict()
            result['code'] = code
            result['language'] = language
            return result
        except requests.exceptions.RequestException as e:
            print(f"Request failed in get_code for {chal_slug}, sub_id {sub_id}: {e}")
            return {'code': None, 'language': None}
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in get_code for {chal_slug}, sub_id {sub_id}: {e}")
            print(f"Response content: {code_res.text}")
            return {'code': None, 'language': None}

    def create_code_file(self, track, sub_domain, filename, code, ext):
        dir = os.path.join(BASE_DIR, self.PREFIX + track, sub_domain)
        file_path = os.path.join(dir, filename + ext)

        if not os.path.exists(dir):
            os.makedirs(dir)
            if not os.path.isfile(file_path):
                print(code, file=open(file_path, 'w'))
        else:
            print(code, file=open(file_path, 'w'))

    # --- Keep your original URL methods HERE ---
    def get_track_url(self, track_name):
        return f"{BASE_URL}tracks/{track_name}/challenges?"

    def get_submissions_url(self, chal_slug):
        return f"{BASE_URL}challenges/{chal_slug}/submissions?"

    def get_particular_submission_url(self, chal_slug, sub_id):
        return f"{BASE_URL}challenges/{chal_slug}/submissions/{sub_id}"
