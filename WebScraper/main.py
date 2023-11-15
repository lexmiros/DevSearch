import time
from website_scrapers.seek_scraper import update_seek_job_data

def main():
    update_seek_job_data()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Tike taken to run {(end_time - start_time) / 60}")