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
JOB_CRITERIA_TEXT = []



# =================================================================================
# LOAD THE LIST OF URLS TO BE SCRAPED
# =================================================================================


def read_json_to_dict(file):
    logging.info("READING JSON FILE TO DICTIONARY...")
    INPUT_PATH = os.path.join("data", "jobs", file)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        data = json.load(json_file)

    for item in data:
        JOB_POSTING_URLS.append(item["url"])


# =================================================================================
# DO THE SCRAPING - PULL JOB DESCRIPTIONS
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
                job_criteria_text = job_criteria_div.get_text(separator=" ", strip=True)
                JOB_CRITERIA_TEXT.append(job_criteria_text)
            elif alt_job_criteria_div:
                job_criteria_alt_text = alt_job_criteria_div.get_text(separator=" ", strip=True)
                JOB_CRITERIA_TEXT.append(job_criteria_alt_text)
            else:
                JOB_CRITERIA_TEXT.append("N/A")
                logging.info(f"JOB CRITERIA NOT FOUND FOR URL {i + 1}: " + str(url))

            progress.update(task, advance=1)
            r.close()
            # time.sleep(config.REQUEST_DELAY)


# =======================================================================================
#   SCRAPE FOR JOB DETAILS - SALARY, HOURS ETC.
# =======================================================================================


# ======================================================================================
# RUN EVERYTHING
# ======================================================================================


def init():
    INPUT_FILE = fh.get_most_recent_item("jobs")
    read_json_to_dict(INPUT_FILE)
    get_job_details()
    for t in JOB_CRITERIA_TEXT:
        logging.info(t)
    output = [{"paragraph": text if text else "NA"} for text in JOB_DESCRIPTIONS_TEXT]
    fh.write_file("jd", output)
    logging.info(f"Saved {len(output)} job descriptions")
