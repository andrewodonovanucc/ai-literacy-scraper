import os
import json
import file_handling as fh
import parse_salary as ps

INPUT_FILE = ""
INPUT_PATH = ""

RAW_JOBS = []
PARSED_JOBS = []

JOB_DESCRIPTIONS_TEXT = []
JOB_SALARY_TEXT = []
JOB_SALARY_LOWER = []
JOB_SALARY_UPPER = []


def get_jobs_from_file():
    global INPUT_FILE, INPUT_PATH
    INPUT_PATH = os.path.join("data", "jobs_linkedin", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        jobs = json.load(json_file)
    return jobs


def deduplicate(JOBS):
    print("IN DEDUPLICATE...")
    print("JOBS INPUTTED: " + str(len(JOBS)))
    seen = set()
    unique = []

    for job in JOBS:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)

    JOBS.clear()
    print("UNIQUE: " + str(len(unique)))
    JOBS.extend(unique)
    print("Unique jobs after deduplication: " + str(len(JOBS)))
    fh.write_file("jobs_linkedin", JOBS)
    print("Saved " + str(len(JOBS)) + " jobs...")


def extract_salary():
    global INPUT_FILE
    INPUT_FILE = fh.get_most_recent_item("jobs_linkedin")
    PARSED_JOBS = get_jobs_from_file()

    print("PARSED JOBS LENGTH: " + str(len(PARSED_JOBS)))
    for job in PARSED_JOBS:
        jd_text = job.get("jd_text", "")

        salary_lower, salary_upper, salary_currency = ps.parse_salary_linkedin(jd_text)

        job["salary_lower"] = salary_lower
        job["salary_upper"] = salary_upper
        job["salary_currency"] = salary_currency

    fh.write_file("criteria_linkedin", PARSED_JOBS)


def init():
    global INPUT_FILE, RAW_JOBS

    INPUT_FILE = fh.get_most_recent_item("jobs_linkedin")
    print("INPUT FILE: " + str(INPUT_FILE))
    RAW_JOBS = get_jobs_from_file()
    deduplicate(RAW_JOBS)
    extract_salary()
