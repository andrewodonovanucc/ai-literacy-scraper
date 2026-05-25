import file_handling as fh
import os
import logging
import pandas as pd 

INPUT_FILE = None
INPUT_PATH = None

JOBS = []

# =================================================================================
# LOAD THE LIST OF URLS TO BE SCRAPED
# =================================================================================


def read_json_to_pandas():
    global INPUT_FILE, INPUT_PATH
    logging.info("READING JSON FILE TO DATAFRAME...")
    jobs = pd.read_json(INPUT_PATH)
    return jobs


# def sort_by_ai_matches(data, descending=True):
#     return sorted(data, key=lambda job: job["ai_matches"], reverse=descending)

# def sort_by_salary(data, descending=True):
#     return sorted(data, key=lambda job: (job["salary_lower"] if job["salary_lower"] is not None else float('-inf')), reverse=descending)



def init():
    global INPUT_FILE, INPUT_PATH
    INPUT_FILE = fh.get_most_recent_item("criteria")
    INPUT_PATH = os.path.join("data", "criteria", INPUT_FILE)


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