import requests
from bs4 import BeautifulSoup
import random
import time

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

def generate_header(user_agent: str) -> dict:
    google_referer_url = (
        "https://www.google.com/search?q=seek&oq=seek&gs_lcrp=EgZjaHJvbWUqCQgAECMYJxiKBTIJCAAQIxgnGIoFMhI"
        "IARAuGEMYxwEYsQMY0QMYigUyCQgCECMYJxiKBTINCAMQABixAxjJAxiABDINCAQQABiSAxixAxiABDIGCAUQRRg8MgYIBhBF"
        "GDwyBggHEEUYPNIBCDE4MDJqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"
    )
    header = {
        "User-Agent": user_agent,
        "Referer" : google_referer_url,
        'Accept-Language': 'en-US,en;q=0.9',
    }

    return header

def scrape_website(url: str, header: dict) -> requests.models.Response:
    header = generate_header()

    session = requests.Session()
    session.headers.update(header)

    response = session.get(url)
    
    return response

def get_job_ids_from_response(response: requests.models.Response) -> list:
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    script_tag = soup.find("script", {"data-automation" : "server-state"})

    print(script_tag.contents[0])



def main():
    website_url = 'https://www.seek.com.au/Software-jobs'
    user_agent = generate_random_user_agent()
    header = generate_header(user_agent)
    response_data = scrape_website(website_url, header)


if __name__ == "__main__":
    main()


