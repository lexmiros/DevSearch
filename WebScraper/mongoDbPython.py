from pymongo import MongoClient
from pymongo.server_api import ServerApi
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

def delete_many_jobs(jobs):
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        db.Jobs.delete_many(jobs)
        client.close()
        logging.info(f"Succesfully deleted {len(jobs)} from db")
    except Exception as error:
        logging.info(f"Failed to delete {len(jobs)} jobs with error {error}")

def get_all_jobs():
    try:
        client = MongoClient(mongoDB_uri)
        db = client["Jobs"]
        all_jobs = db.Jobs.find()
        client.close()

        logging.info(f"Succesfully found {len(all_jobs)} jobs in db")

        return all_jobs
    
    except Exception as error:
        logging.info(f"Failed to get jobs from db")



    
if __name__ == "__main__":
    insert_single_job({"test":"test"})

