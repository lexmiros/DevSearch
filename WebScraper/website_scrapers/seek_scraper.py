import json
import logging
from bs4 import BeautifulSoup
from db_connector import insert_many_jobs, get_all_job_ids_and_return_as_list, delete_many_jobs_on_job_id
from common_utils import generate_request_header, make_request, get_nested_value, return_all_ids_found_in_db_not_in_scrape, return_all_ids_found_in_scrape_not_in_db, return_all_unique_job_ids, remove_html_tags_from_text


logging.basicConfig(level=logging.INFO)

SEEK_BASE_URL = "https://www.seek.com.au/"
SEEK_SOFTWARE_DEVELOPER_URL = "Software-Developer-jobs/"
SEEK_IT_ENGINEERING_SCIENCE_CLASSIFICATION_CODE = "?classification=6281%2C1209%2C1223"

MAX_PAGES = 1

def extract_job_ids_from_response(response):
    """Extract job IDs from a single page SEEK response."""
    if not response:
        return None
    try:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        script_element_text = soup.find(
            "script", {"data-automation": "server-state"}).get_text(strip=True)

        if not script_element_text:
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
        regional_url = f"{SEEK_BASE_URL}{SEEK_SOFTWARE_DEVELOPER_URL}{region}{SEEK_IT_ENGINEERING_SCIENCE_CLASSIFICATION_CODE}"
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
    """Convert job listing data response to JSON."""
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    script_element_text = soup.find(
        "script", {"data-automation": "server-state"}).get_text(strip=True)
    
    start_index = script_element_text.find("window.SEEK_REDUX_DATA = ") + len("window.SEEK_REDUX_DATA = ")
    end_index = script_element_text.find("};", start_index) + 1

    json_data = script_element_text[start_index:end_index].strip()
    
    while "undefined" in json_data:
        json_data = json_data.replace("undefined", '"N/A"')

    seek_config_dict = json.loads(json_data)

    return seek_config_dict

def get_apply_link_from_request_response(response):
    """Get apply link from request response."""
    html_code = response.text
    soup = BeautifulSoup(html_code, 'html.parser')

    div_element = soup.find('div', class_='_1wkzzau0 a1msqip _126xumx0')

    if div_element:
        anchor_element = div_element.find('a')
        if anchor_element:
            href_link = anchor_element.get('href')
            return f"seek.com.au/{href_link}"
        else:
            logging.warning("No anchor tag found within the div.")
    else:
        logging.warning("Div with specified class not found.")

    return None

def get_job_details_for_job_id(job_id):
    """Get job details for a specific job ID."""
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
    job_description_with_html = get_nested_value(job_details, ["content"])
    job_description_without_html = remove_html_tags_from_text(job_description_with_html)

    return {
        "job_id": job_id,
        "apply_link": job_quick_apply_link,
        "location": job_location,
        "employment_type": job_employement_type,
        "advertiser": job_advertiser,
        "salary": job_salary,
        "listed_duration": job_listed_duration,
        "classification": job_classification,
        "sub_classification": job_sub_classification,
        "employer_questions": job_employer_questions,
        "description_with_html": job_description_with_html,
        "description_without_html": job_description_without_html
    }

def get_job_details_for_list_of_job_ids(job_ids):
    """Get job details for a list of job IDs."""
    jobs = []
    job_counter = 1
    number_of_ids = len(job_ids)

    for job_id in job_ids:
        logging.info(f"Getting job information for job {job_id} (job {job_counter} of {number_of_ids})")

        try:
            jobs.append(get_job_details_for_job_id(job_id))
        except Exception as e:
            logging.error(f"Failed to get job data for job {job_id} (job {job_counter} of {number_of_ids}): {e}")

        job_counter += 1

    return jobs

def update_seek_job_data():
    """Update Seek job data in the database."""
    seek_job_ids = iterate_over_seek_pages_to_get_job_ids()
    seek_job_ids = return_all_unique_job_ids(seek_job_ids)
    job_ids_in_db = get_all_job_ids_and_return_as_list()

    seek_job_ids_not_in_db = return_all_ids_found_in_scrape_not_in_db(seek_job_ids, job_ids_in_db)
    seek_job_data = get_job_details_for_list_of_job_ids(seek_job_ids_not_in_db)
    insert_many_jobs(seek_job_data)

    db_ids_not_in_seek_ids = return_all_ids_found_in_db_not_in_scrape(seek_job_ids, job_ids_in_db)
    delete_many_jobs_on_job_id(db_ids_not_in_seek_ids)
