# =================================================================================
# IMPORTS
# =================================================================================

import file_handling as fh
import config
import json
import requests
from rich.progress import Progress
from bs4 import BeautifulSoup as bs
import os
import logging
import parse_salary as ps

# =================================================================================
# VARIABLES FOR FILE HANDLING
# =================================================================================

INPUT_FILE = None
INPUT_PATH = None

# =================================================================================
# ARRAY CONTAINERS
# =================================================================================

JOB_POSTING_URLS = []
JOB_DESCRIPTIONS_DIV = []
JOB_DESCRIPTIONS_TEXT = []

JOB_CRITERIA_DIV = []

JOB_SALARY_STRING = []
JOB_SALARY_LOWER = []
JOB_SALARY_UPPER = []
JOB_HOURS = []
JOB_CONTRACT = []
JOB_DATE_POSTED = []
JOB_DATE_CLOSES = []

JOB_IS_PHD = []


# =================================================================================
# LOAD THE LIST OF URLS TO BE SCRAPED
# =================================================================================


def read_json_to_dict():
    logging.info("READING JSON FILE TO DICTIONARY...")
    jobs = get_jobs_from_file()

    for item in jobs:
        JOB_POSTING_URLS.append(item["url"])


# =================================================================================
# READ THE JOBS FROM THE JSON FILE IN THE JOBS FOLDER
# =================================================================================


def get_jobs_from_file():
    global INPUT_FILE, INPUT_PATH
    INPUT_PATH = os.path.join("data", "jobs", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        jobs = json.load(json_file)
    return jobs

# =================================================================================
# DO THE SCRAPING - PULL JOB DESCRIPTIONS AND CRITERIA
# =================================================================================

def get_job_details():
    logging.info("=" * 100)
    logging.info("GETTING JOB DETAILS...")

    total = len(JOB_POSTING_URLS)
    logging.info("TOTAL POTENTIAL JOB DESCRIPTIONS AND CRITERIA: " + str(total))
    logging.info("=" * 100)

    with Progress() as progress:
        task = progress.add_task("FETCHING JOB DETAILS...", total=total)
        for i, url in enumerate(JOB_POSTING_URLS):
            r = requests.get(url, timeout=60, headers=config.HEADERS)
            if r.status_code != 200:
                logging.info("Request failed")
            soup = bs(r.text, "html.parser")

            #   JOB DESCRIPTIONS
            jd_div = soup.find("div", id="job-description")
            alt_jd_div = soup.find(
                "div", class_="col-lg-8 col-md-12 mb-4 order-2 order-lg-1"
            )

            if jd_div:
                jd_text = jd_div.get_text(separator=" ", strip=True)
                JOB_DESCRIPTIONS_TEXT.append(jd_text)
            elif alt_jd_div:
                alt_jd_text = alt_jd_div.get_text(separator=" ", strip=True)
                JOB_DESCRIPTIONS_TEXT.append(alt_jd_text)
            else:
                JOB_DESCRIPTIONS_TEXT.append("N/A")
                logging.info(f"JOB DESCRIPTION NOT FOUND FOR URL {i + 1}: " + str(url))

            #   JOB CRITERIA
            job_criteria_div = soup.find("div", class_="j-advert-details__container")
            alt_job_criteria_div = soup.find(
                "div", class_="col-lg-4 col-md-12 mb-4 order-1 order-lg-2"
            )
            
            if job_criteria_div:
                JOB_CRITERIA_DIV.append(job_criteria_div)
            elif alt_job_criteria_div:
                JOB_CRITERIA_DIV.append(alt_job_criteria_div)
            else:
                JOB_CRITERIA_DIV.append("N/A")
                logging.info(f"JOB CRITERIA NOT FOUND FOR URL {i + 1}: " + str(url))

            progress.update(task, advance=1)
            r.close()
            # time.sleep(config.REQUEST_DELAY)

    extract_criteria_fields()
    export_job_descriptions()
    export_criteria()

# =================================================================================
# EXTRACT THE JOB CRITERIA FIELDS FROM THE HTML TABLE STRUCTURE
# =================================================================================

def extract_criteria_fields():
    for i, div in enumerate(JOB_CRITERIA_DIV):
        salary_lower = None
        salary_upper = None
        hours = "N/A"
        contract = "N/A"
        date_posted = "N/A"
        date_closes = "N/A"
 
        if div == "N/A":
            JOB_SALARY_LOWER.append(salary_lower)
            JOB_SALARY_UPPER.append(salary_upper)
            JOB_HOURS.append(hours)
            JOB_CONTRACT.append(contract)
            continue
 
        for row in div.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            
            if not th or not td:
                continue
            header = th.get_text(strip=True)
            value = td.get_text(separator=" ", strip=True)
            if header == "Salary:":
                raw_salary = ' '.join(value.split())
                salary_lower, salary_upper = ps.parse_salary_bounds(raw_salary)
            elif header == "Hours:":
                hours = value
            elif header == "Contract Type:":
                contract = value
            elif header == "Placed On:":
                date_posted = value
            elif header == "Closes:" or header == "Expires:":
                date_closes = value

        JOB_SALARY_STRING.append(raw_salary)
        JOB_SALARY_LOWER.append(salary_lower)
        JOB_SALARY_UPPER.append(salary_upper)
        JOB_HOURS.append(hours)
        JOB_CONTRACT.append(contract)
        JOB_DATE_POSTED.append(date_posted)
        JOB_DATE_CLOSES.append(date_closes)

    logging.info(f"Extracted criteria for {len(JOB_CRITERIA_DIV)} jobs.")

# =================================================================================
# Check if the job is a PhD role by looking for "PhD" in the title or description.
# =================================================================================

def is_phd_role():
    jobs = get_jobs_from_file()
    for job in jobs:
        title = job.get("title", "").lower()
        description = job.get("jd_text", "").lower()
        if "phd" in title or "phd" in description:
            JOB_IS_PHD.append(True)
        else:
            JOB_IS_PHD.append(False)

# =================================================================================
# EXPORT THE JOB DESCRIPTIONS TO JSON IN JD FOLDER.
# =================================================================================

def export_job_descriptions():
    global INPUT_PATH, INPUT_FILE
    logging.info("EXPORTING JOB DESCRIPTIONS...")
    logging.info("=" * 100)
    # output = [{"paragraph": text if text else "NA"} for text in JOB_DESCRIPTIONS_TEXT]
    # fh.write_file("jd", output)

    jobs = get_jobs_from_file()
    
    for i, job in enumerate(jobs):
        job["jd_text"] = JOB_DESCRIPTIONS_TEXT[i] if i < len(JOB_DESCRIPTIONS_TEXT) else "N/A"
    
    
    fh.write_file("jd", jobs)
    logging.info("=" * 100)
    logging.info(f"Saved {len(jobs)} Job Descriptions.")
    logging.info("=" * 100)

# =================================================================================
# EXPORT THE JOB DETAILS TO JSON IN CRITERIA FOLDER.
# =================================================================================

def export_criteria():
    logging.info("=" * 100)
    logging.info("EXPORTING CRITERIA...")

    file = fh.get_most_recent_item("jd")
    filepath = os.path.join("data", "jd", file)
    with open(filepath, encoding="utf-8") as json_file:
        jobs = json.load(json_file)
    
    for i, job in enumerate(jobs):
        job["salary_text"] = JOB_SALARY_STRING[i] if i < len(JOB_SALARY_STRING) else "N/A"
        job["salary_lower"] = JOB_SALARY_LOWER[i] if i < len(JOB_SALARY_LOWER) else None
        job["salary_upper"] = JOB_SALARY_UPPER[i] if i < len(JOB_SALARY_UPPER) else None
        job["hours"] = JOB_HOURS[i] if i < len(JOB_HOURS) else "N/A"
        job["contract_type"] = JOB_CONTRACT[i] if i < len(JOB_CONTRACT) else "N/A"
        job["date_posted"] = JOB_DATE_POSTED[i] if i < len(JOB_DATE_POSTED) else "N/A"
        job["date_closes"] = JOB_DATE_CLOSES[i] if i < len(JOB_DATE_CLOSES) else "N/A"
        job["is_phd"] = JOB_IS_PHD[i] if i < len(JOB_IS_PHD) else False

    fh.write_file("criteria", jobs)
    logging.info("=" * 100)
    logging.info(f"Saved {len(jobs)} Criteria.")
    logging.info(f"{len(JOB_IS_PHD)} PhD roles out of {len(jobs)} identified.")
    logging.info("=" * 100)



# ======================================================================================
# RUN EVERYTHING
# ======================================================================================

def init():
    global INPUT_FILE, INPUT_PATH
    INPUT_FILE = fh.get_most_recent_item("jobs")
    INPUT_PATH = os.path.dirname(INPUT_FILE)
    logging.info("GETTING UP TO DATE CURRENCY RATES...")
    ps.get_updated_currency_rates()
    logging.info("EXTRACTING CRITERIA FIELDS...")
    read_json_to_dict()
    get_job_details()
    
