import time
from website_scrapers.seek_scraper import update_seek_job_data
from db_connector import delete_all_jobs

def main():
    update_seek_job_data()
    #delete_all_jobs()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time taken to run {(end_time - start_time) / 60}")