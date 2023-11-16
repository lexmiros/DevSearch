import time
import requests
import random
import logging

from bs4 import BeautifulSoup

SLEEP_DURATION_RANGE = (1, 2)

class Non200ResponseError(Exception):
    pass

def generate_random_user_agent() -> str:
    """Generate a random user agent string."""
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
    """Generate headers for HTTP requests."""
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
    """Make an HTTP GET request to the specified URL with the given headers."""
    try:
        session = requests.Session()
        session.headers.update(header)
        response = session.get(url)

        if response.status_code != 200:
            raise Non200ResponseError(
                f"Non-200 response: {response.status_code}")
        
        sleep_duration = random.uniform(*SLEEP_DURATION_RANGE)
        time.sleep(sleep_duration)

        return response
    except requests.exceptions.RequestException as exception:
        logging.error(f"Request failed: {exception}")
        return None
    
def get_nested_value(data, keys, default="Not available"):
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default
    
def return_all_ids_found_in_scrape_not_in_db(job_ids_in_scrape, job_ids_in_db):
    return [job_id for job_id in job_ids_in_scrape if job_id not in job_ids_in_db]

def return_all_ids_found_in_db_not_in_scrape(job_ids_in_scrape, job_ids_in_db):
    return [job_id for job_id in job_ids_in_db if job_id not in job_ids_in_scrape]

def return_all_unique_job_ids(job_ids):
    return set(job_ids)

def remove_html_tags_from_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ")