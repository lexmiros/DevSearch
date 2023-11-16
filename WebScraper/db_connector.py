from pymongo import MongoClient

from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

mongoDB_uri = os.getenv("MONGO_DB_URI_RAW")
client = MongoClient(mongoDB_uri)

def insert_single_job(job):
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        db.Jobs.insert_one(job)
        client.close()
        logging.info(f"Succesfully added {job.job_id} to db")
    except Exception as error:
        logging.info(f"Failed to add job {job.job_id} with error {error}")

def insert_many_jobs(jobs):
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        db.Jobs.insert_many(jobs)
        client.close()
        logging.info(f"Succesfully added {len(jobs)} to db")
    except Exception as error:
        logging.info(f"Failed to add {len(jobs)} jobs with error {error}")

def delete_single_job(job):
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        db.Jobs.delete_one()
        client.close()
        logging.info(f"Succesfully deleted {job.job_id} from db")
    except Exception as error:
        logging.info(f"Failed to delete job {job.job_id} with error {error}")

def delete_many_jobs_on_job_id(job_ids):
    try:
        job_ids_dict = {"job_id": {"$in": job_ids}}
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        result = db.Jobs.delete_many(job_ids_dict)
        client.close()
        logging.info(f"Succesfully deleted {result.deleted_count} jobs from db")
    except Exception as error:
        logging.info(f"Failed to delete {result.deleted_count} jobs with error {error}")

def delete_all_jobs():
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        result = db.Jobs.delete_many({})
        client.close()
        logging.info(f"Succesfully deleted {result.deleted_count} jobs from db")
    except Exception as error:
        logging.info(f"Failed to delete {result.deleted_count} jobs with error {error}")

def get_all_jobs_and_return_as_list():
    jobs = []

    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        all_jobs = db.Jobs.find()
        
        for job in all_jobs:
            jobs.append(job)

        client.close()

        logging.info(f"Succesfully found {len(jobs)} jobs in db")
    
    except Exception as error:
        logging.info(f"Failed to get jobs from db: {error}")
    
    return jobs

def get_all_job_ids_and_return_as_list():
    job_ids = []

    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        all_jobs = db.Jobs.find()
        
        for job in all_jobs:
            job_ids.append(job["job_id"])

        client.close()

        logging.info(f"Succesfully found {len(job_ids)} job ids in db")
    
    except Exception as error:
        logging.info(f"Failed to get job ids from db: {error}")
    
    return job_ids


