from bs4 import BeautifulSoup

import time
import requests
import random
import json


class Non200ResponseError(Exception):
    pass


def generate_random_user_agent() -> str:
    platforms = [
        'Windows NT 10.0; Win64; x64',
        'Windows NT 6.1; Win64; x64',
        'Macintosh; Intel Mac OS X 10_15_7',
        'Linux; Android 11; Pixel 4 XL',
        'iPhone; CPU iPhone OS 14_6 like Mac OS X',
        'iPad; CPU OS 14_6 like Mac OS X',
    ]

    browsers = [
        'Chrome/91.0.4472.124 Safari/537.36',
        'Firefox/89.0',
        'Edg/91.0.864.37',
        'Safari/537.36',
        'Mobile Safari/537.36',
    ]

    return f'Mozilla/5.0 ({random.choice(platforms)}) AppleWebKit/537.36 ({random.choice(browsers)})'


def generate_request_header() -> dict:
    user_agent = generate_random_user_agent()
    google_referer_url = (
        "https://www.google.com/search?q=seek&oq=seek&gs_lcrp=EgZjaHJvbWUqCQgAECMYJxiKBTIJCAAQIxgnGIoFMhI"
        "IARAuGEMYxwEYsQMY0QMYigUyCQgCECMYJxiKBTINCAMQABixAxjJAxiABDINCAQQABiSAxixAxiABDIGCAUQRRg8MgYIBhBF"
        "GDwyBggHEEUYPNIBCDE4MDJqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"
    )
    header = {
        "User-Agent": user_agent,
        "Referer": google_referer_url,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    return header


def make_request(url: str, header: dict) -> requests.models.Response:
    try:
        session = requests.Session()
        session.headers.update(header)
        response = session.get(url)

        if response.status_code != 200:
            raise Non200ResponseError(
                f"Non-200 response: {response.status_code}")

        return response
    except requests.exceptions.RequestException as exception:
        print(f"Request failed: {exception}")
        return None


def extract_job_ids_from_response(response: requests.models.Response) -> list:
    if not response:
        return None
    try:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        script_element_text = soup.find(
            "script", {"data-automation": "server-state"}).get_text(strip=True)

        if script_element_text is None:
            raise ValueError("Script element not found")

        start_index = script_element_text.find('"jobIds"') + len('"jobIds:"')

        if start_index < len('"jobIds:"'):
            raise ValueError("Job IDs not found in script")

        end_index = script_element_text.find(']', start_index) + 1
        job_ids_str = script_element_text[start_index:end_index]
        job_ids = json.loads(job_ids_str)

        return job_ids

    except (AttributeError, ValueError, json.JSONDecodeError) as e:
        print(f"An error occurred: {e}")
        return None


def iterate_over_seek_pages_to_get_job_ids(base_url):
    all_job_ids = []
    regions = ["in-Queensland-QLD", "in-New-South-Wales-NSW", "in-Victoria-VIC", "in-Western-Australia-WA", "in-Tasmania-TAS", "in-Australian-Capital-Territory-ACT", "in-South-Australia-SA"]

    #Seek currently stops showing results after page 25
    #Break down searches into regions to capture more results
    for region in regions:
        max_pages = 5
        page_number = 1
        regional_url = f"{base_url}{region}"
        found_properties = True

        print(f"Attempting to get results for region: {region}")

        while page_number < max_pages and found_properties:
            print(f"Attempting to get results from page {page_number}")
            sleep_duration = random.uniform(2, 6)

            current_url = f"{regional_url}?page={page_number}"
            print(current_url)
            header = generate_request_header()
            response = make_request(current_url, header)
            job_ids = extract_job_ids_from_response(response)

            if not job_ids:
                print(f"No job ids found for page {page_number}")
                print("Breaking out of loop")
                found_properties = False

            all_job_ids.extend(job_ids)
            page_number += 1
            print("Job ids found, moving onto next page")
            time.sleep(sleep_duration)

    print(f"{len(all_job_ids)} job ids found")

    return all_job_ids


def main():
    website_url = 'https://www.seek.com.au/Software-Developer-jobs/'
    x = iterate_over_seek_pages_to_get_job_ids(website_url)

if __name__ == "__main__":
    main()
