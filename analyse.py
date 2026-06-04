from altair.datasets import data

import file_handling as fh
import os
import json
import logging
import pandas as pd 

INPUT_FILE = None
INPUT_PATH = None

JOBS_FROM_JSON = []

# =================================================================================
# LOAD THE JOBS FROM THE MOST RECENT CRITERIA FILE
# =================================================================================

def get_jobs_from_file():
    global JOBS_FROM_JSON
    INPUT_FILE = fh.get_most_recent_item("criteria")
    INPUT_PATH = os.path.join("data", "criteria", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        JOBS_FROM_JSON = json.load(json_file)
    update_jobs_with_links()

 # =================================================================================
# UPDATE THE JOBS WITH LINK MARKDOWN FOR STREAMLIT
# =================================================================================  

def update_jobs_with_links():
    global JOBS_FROM_JSON
    for job in JOBS_FROM_JSON:
        # print(job["url"])
        job["url"] = "[LINK](" + job["url"] + ")"
        # print(job["url"])

    fh.write_file("analyse", JOBS_FROM_JSON)


# =================================================================================
# LOAD THE UPDATED JOBS FROM JSON TO PANDAS
# =================================================================================

def read_json_to_pandas():
    get_jobs_from_file()
    INPUT_FILE = fh.get_most_recent_item("analyse")
    INPUT_PATH = os.path.join("data", "analyse", INPUT_FILE)
    logging.info("READING JSON FILE TO DATAFRAME...")
    jobs = pd.read_json(INPUT_PATH)
    jobs.drop(columns=["salary_text", "jd_text"], inplace=True)
    return jobs


# def sort_by_ai_matches(data, descending=True):
#     return sorted(data, key=lambda job: job["ai_matches"], reverse=descending)

# def sort_by_salary(data, descending=True):
#     return sorted(data, key=lambda job: (job["salary_lower"] if job["salary_lower"] is not None else float('-inf')), reverse=descending)

def init():
    read_json_to_pandas()

    # read_ai_jobs()
    # sorted_jobs = sort_by_ai_matches(JOBS)
    # for job in sorted_jobs:
    #     if job['ai_matches'] > 2:
    #         print(f"{job['ai_matches']:>3} matches | {job['title']}")
    # sorted_jobs = sort_by_salary(JOBS)
    # for job in sorted_jobs:
    #     if job['salary_lower'] is not None and job['salary_lower'] > 10000:
    #         print(f"{job['salary_lower'] if job['salary_lower'] is not None else 'N/A':>10} EUR | {job['title']}")
    
    # dataFrame = pd.read_json(&quot;subject.json&quot;)
    # print(dataFrame)