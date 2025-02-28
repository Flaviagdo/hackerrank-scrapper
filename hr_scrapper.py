import requests
from urls_service import UrlService  # Keep your UrlService
from credentials import CSRF_TOKEN, COOKIE  # Keep your credentials
import json
import time
import os  # Import os for file handling
from util import get_file_extension  # Keep your utility functions
from models import get_code_result_model #keep your models
from constants import BASE_DIR # Keep your contants


class HR_Scrapper:
    def __init__(self, base_delay=2):
        self.url_service = UrlService()  # Use your UrlService
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
        # --- INTEGRATE YOUR LOGIC HERE ---
        url = self.url_service.get_track_url(track) # Get the Track URL
        try:
            response = requests.get(url, headers=self.headers) # Make the request with headers
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            tracks = response.json()  # Use .json() for parsing
            models = tracks['models']
            for i in models:
                chal_slug = i.get('slug')
                sub_domain = i.get('track').get('slug')
                if chal_slug is None:
                    raise Exception("Chal_slug:" + str(chal_slug))

                sub_domain_string = "Domain: " + sub_domain
                print(track + " " + sub_domain_string + chal_slug.rjust(70 - len(sub_domain_string)))

                sub_id = self.get_submissions(chal_slug)  # Call your get_submissions method
                code = False
                if sub_id:
                    result = self.get_code(chal_slug, sub_id)  # Call your get_code method
                    code = result['code']
                    lang = result['language']

                if code:
                    ext = get_file_extension(track, lang)
                    self.create_code_file(track, sub_domain, chal_slug, code, ext) #Call create_code_file
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {track}: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error for {track}: {e}")
            print(f"Response content: {response.text}")
        finally:
            time.sleep(self.base_delay)

    # --- KEEP YOUR OTHER METHODS (with modifications for headers)---

    def get_submissions(self, chal_slug):
        # Add headers to this request as well
        url = self.url_service.get_submissions_url(chal_slug) #get submission url
        try:
            submissions = requests.get(url, headers=self.headers) #get request adding headers
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
        # And here
        url = self.url_service.get_particular_submission_url(chal_slug, sub_id)  #get submission url
        try:
            code_res = requests.get(url, headers=self.headers)  #get request adding headers
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
            return {'code': None, 'language': None}  # Return None values on error
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in get_code for {chal_slug}, sub_id {sub_id}: {e}")
            print(f"Response content: {code_res.text}")
            return {'code': None, 'language': None}

    def create_code_file(self, track, sub_domain, filename, code, ext):
        # This method stays mostly the same, it's your original logic
        dir = os.path.join(BASE_DIR, self.PREFIX + track, sub_domain)
        file_path = os.path.join(dir, filename + ext)

        if not os.path.exists(dir):  # os.path.isdir(dir):
            os.makedirs(dir)
            if not os.path.isfile(file_path):
                print(code, file=open(file_path, 'w'))
        else:
            print(code, file=open(file_path, 'w'))

    # Add url methods
    def get_track_url(self, track_name):
        return f"https://www.hackerrank.com/rest/contests/master/tracks/{track_name}/challenges?"

    def get_submissions_url(self, chal_slug):
        return f"https://www.hackerrank.com/rest/contests/master/challenges/{chal_slug}/submissions?"

    def get_particular_submission_url(self, chal_slug, sub_id):
        return f"https://www.hackerrank.com/rest/contests/master/challenges/{chal_slug}/submissions/{sub_id}"
