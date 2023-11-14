from bs4 import BeautifulSoup
from mongoDbPython import insert_single_job, insert_many_jobs, get_all_jobs_and_return_as_list, get_all_job_ids_and_return_as_list
import time
import requests
import random
import json
import logging

logging.basicConfig(level=logging.INFO)

SEEK_BASE_URL = "https://www.seek.com.au/"
SEEK_SOFTWARE_DEVELOPER_BASE_URL = f"{SEEK_BASE_URL}Software-Developer-jobs/"
SLEEP_DURATION_RANGE = (1, 2)
MAX_PAGES = 1

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

def extract_job_ids_from_response(response: requests.models.Response) -> list:
    """Extract job IDs from the response."""
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
        logging.error(f"An error occurred: {e}")
        return None

def iterate_over_seek_pages_to_get_job_ids():
    """Iterate over Seek pages to get job IDs for different regions."""
    all_job_ids = []
    regions = ["in-Queensland-QLD", "in-New-South-Wales-NSW", "in-Victoria-VIC", "in-Western-Australia-WA", "in-Tasmania-TAS", "in-Australian-Capital-Territory-ACT", "in-South-Australia-SA"]

    for region in regions:
        page_number = 1
        regional_url = f"{SEEK_SOFTWARE_DEVELOPER_BASE_URL}{region}"
        found_properties = True

        logging.info(f"Attempting to get results for region: {region}")

        while page_number <= MAX_PAGES and found_properties:
            logging.info(f"Attempting to get results from page {page_number}")

            current_url = f"{regional_url}?page={page_number}"

            logging.info(current_url)

            header = generate_request_header()
            response = make_request(current_url, header)
            job_ids = extract_job_ids_from_response(response)

            if not job_ids:
                logging.info(f"No job ids found for page {page_number}")
                logging.info("Breaking out of loop")
                found_properties = False

            all_job_ids.extend(job_ids)
            page_number += 1
            logging.info("Job ids found, moving onto next page")
            
    logging.info(f"{len(all_job_ids)} job ids found")

    return all_job_ids

def convert_job_listing_data_response_to_json(response):
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    script_element_text = soup.find(
        "script", {"data-automation": "server-state"}).get_text(strip=True)
    
    #Find the start and end of data needed
    start_index = script_element_text.find("window.SEEK_REDUX_DATA = ") + len("window.SEEK_REDUX_DATA = ")
    end_index = script_element_text.find("};", start_index) + 1

    json_data = script_element_text[start_index:end_index].strip()
    
    #Missing values marked as undefined without quotes breaking json formatting
    while "undefined" in json_data:
        json_data = json_data.replace("undefined", '"N/A"')

    seek_config_dict = json.loads(json_data)

    return seek_config_dict

def get_nested_value(data, keys, default="Not available"):
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default

def get_apply_link_from_request_response(response):
    html_code = response.text

    soup = BeautifulSoup(html_code, 'html.parser')

    # Find the div with the specified class
    div_element = soup.find('div', class_='_1wkzzau0 a1msqip _126xumx0')

    # Extract the href attribute from the anchor tag within the div
    if div_element:
        anchor_element = div_element.find('a')
        if anchor_element:
            href_link = anchor_element.get('href')

        else:
            print("No anchor tag found within the div.")
    else:
        print("Div with specified class not found.")
    
    return f"seek.com.au/{href_link}"
    

def get_job_details_for_job_id(job_id):
    url = f"{SEEK_BASE_URL}job/{job_id}"
    header = generate_request_header()
    response = make_request(url, header)
    json_job_data = convert_job_listing_data_response_to_json(response)
    
    job_details = json_job_data["jobdetails"]["result"]["job"]

    job_quick_apply_link = get_apply_link_from_request_response(response)
    job_location = get_nested_value(job_details, ["location", "label"])
    job_employement_type = get_nested_value(job_details, ["workTypes", "label"])
    job_advertiser = get_nested_value(job_details, ["advertiser", "name"])
    job_salary = get_nested_value(job_details, ["salary", "label"])
    job_listed_duration = get_nested_value(job_details, ["listedAt", "shortLabel"])
    job_classification = get_nested_value(job_details, ["tracking", "classificationInfo", "classification"])
    job_sub_classification = get_nested_value(job_details, ["tracking", "classificationInfo", "subClassification"])
    job_employer_questions = get_nested_value(job_details, ["products", "questionnaire", "questions"])
    job_description = get_nested_value(job_details, ["content"])

    return {
        "job_id": job_id,
        "apply_link" : job_quick_apply_link,
        "location": job_location,
        "employment_type": job_employement_type,
        "advertiser": job_advertiser,
        "salary": job_salary,
        "listed_duration": job_listed_duration,
        "classification": job_classification,
        "sub_classification": job_sub_classification,
        "employer_questions": job_employer_questions,
        "description": job_description
    }

def get_job_details_for_all_job_ids(job_ids):
    jobs = []
    counter = 1
    number_of_ids = len(job_ids)

    for id in job_ids:
        logging.info(f"Getting job information for job {id} (job {counter} of {number_of_ids})")

        try:
            jobs.append(get_job_details_for_job_id(id))
        except:
            logging.info(f"Failed to get job data for job {id} (job {counter} of {number_of_ids})")

        counter += 1

    return jobs
     

def main():
    """Main function to initiate the job ID retrieval process."""
    # job_ids = iterate_over_seek_pages_to_get_job_ids()
    
    # jobs = get_job_details_for_all_job_ids(job_ids)
    # insert_many_jobs(jobs)
    print(get_all_job_ids_and_return_as_list()[0])


if __name__ == "__main__":
    main()
    

