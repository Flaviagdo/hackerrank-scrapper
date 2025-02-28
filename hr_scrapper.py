import requests
from urls_service import UrlService
from credentials import CSRF_TOKEN, COOKIE
import json
import time
import os
from util import get_file_extension
from models import get_code_result_model
from constants import BASE_DIR, BASE_URL


class HR_Scrapper:
    def __init__(self, base_delay=2):
        self.url_service = UrlService.instance()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Cookie": COOKIE,
            "x-csrf-token": CSRF_TOKEN,
            "accept": "application/json",
            "content-type": "application/json",
            "referer": "https://www.hackerrank.com/submissions/all"
        }
        self.base_delay = base_delay
        self.PREFIX = "__"

    def get_track(self, track):
        url = self.get_track_url(track)  # Use HR_Scrapper's methods
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tracks = response.json()
            models = tracks['models']
            for challenge in models:  # Iterate through each challenge
                chal_slug = challenge.get('slug')
                sub_domain = challenge.get('track').get('slug')
                if chal_slug is None:
                    raise Exception("Chal_slug:" + str(chal_slug))

                sub_domain_string = "Domain: " + sub_domain
                print(track + " " + sub_domain_string + chal_slug.rjust(70 - len(sub_domain_string)))

                # Get ALL submissions for the current challenge (using pagination)
                for sub_id in self.get_all_submissions(chal_slug):
                    code = False
                    if sub_id:
                        result = self.get_code(chal_slug, sub_id)
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

    def get_all_submissions(self, chal_slug):
        """Gets all submissions for a given challenge, handling pagination."""
        all_submission_ids = []
        offset = 0
        limit = 20  # Or whatever the API's limit is
        while True:
            url = self.get_submissions_url(chal_slug, offset, limit)  # Modified get_submissions_url
            try:
                submissions = requests.get(url, headers=self.headers)
                submissions.raise_for_status()
                data = submissions.json()
                models = data['models']

                if not models:  # No more submissions
                    break

                for submission in models:
                    all_submission_ids.append(submission['id'])

                offset += limit  # Increment offset for the next page

            except requests.exceptions.RequestException as e:
                print(f"Request failed in get_all_submissions for {chal_slug}: {e}")
                break  # Stop if there's a request error
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error in get_all_submissions for {chal_slug}: {e}")
                print(f"Response content: {submissions.text}")
                break  # Stop if there's a JSON error
            finally:
                time.sleep(self.base_delay)
        return all_submission_ids

    def get_code(self, chal_slug, sub_id):
        url = self.get_particular_submission_url(chal_slug, sub_id)
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


    # --- URL methods (Modified for pagination) ---
    def get_track_url(self, track_name):
        return f"{BASE_URL}tracks/{track_name}/challenges?"

    def get_submissions_url(self, chal_slug, offset=0, limit=20):
        # Include offset and limit in the URL
        return f"{BASE_URL}challenges/{chal_slug}/submissions?offset={offset}&limit={limit}"

    def get_particular_submission_url(self, chal_slug, sub_id):
        return f"{BASE_URL}challenges/{chal_slug}/submissions/{sub_id}"
