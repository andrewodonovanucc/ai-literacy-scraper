# =================================================================================
# IMPORTS
# =================================================================================

import file_handling as fh
from config import HEADERS
import json
from datetime import datetime as dt
import time as time_module
import logging
import re
import requests
from rich.progress import Progress
from bs4 import BeautifulSoup as bs
import os
import parse_salary as ps
import helper as hp

# =================================================================================
# VARIABLES FOR FILE HANDLING
# =================================================================================

INPUT_FILE = None
INPUT_PATH = None

# =================================================================================
# ARRAY CONTAINERS
# =================================================================================

JOB_POSTING_URLS = []
JOB_POSTING_TITLES = []
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
JOB_FTE_VALUE = []
JOB_DISCIPLINE = []

JOB_IS_PHD = []
JOB_IS_CLOSED = []

LOCATION_DIV = []


# =================================================================================
# LOAD THE LIST OF URLS TO BE SCRAPED
# =================================================================================


def read_json_to_dict():
    logging.info("READING JSON FILE TO DICTIONARY...")
    jobs = get_jobs_from_file()

    for item in jobs:
        JOB_POSTING_URLS.append(item["url"])
        JOB_POSTING_TITLES.append(item.get("title", ""))


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
    session = requests.Session()
    session.headers.update(HEADERS)

    logging.info("STARTED SESSION...")
    logging.info("=" * 100)

    with Progress() as progress:
        task = progress.add_task("FETCHING JOB DETAILS...", total=total)
        for i, url in enumerate(JOB_POSTING_URLS):
            time_module.sleep(1)

            randomised_url = url + f"?_={int(time_module.time())}"
            r = hp.request_page(session, randomised_url, label=f"job {i + 1}")
            if r is None:
                # Append N/A placeholders to keep list alignment intact
                JOB_DESCRIPTIONS_TEXT.append("N/A")
                JOB_CRITERIA_DIV.append("N/A")
                LOCATION_DIV.append("N/A")
                JOB_DISCIPLINE.append("N/A")
                JOB_IS_PHD.append(False)
                JOB_POSTING_URLS[i] = None
                progress.update(task, advance=1)
                continue

            soup = bs(r.text, "html.parser")
            r.close()

            # Remove non-Academic or Research roles
            job_type_inputs = soup.find_all(
                "input", class_="j-form-input__disabled-cat"
            )
            job_types = [inp.get("value", "") for inp in job_type_inputs]
            if "Academic or Research" not in job_types:
                logging.info(
                    f"\nSKIPPED (not Academic or Research) URL {i + 1}: {url}\n"
                )
                JOB_POSTING_URLS[i] = None
                progress.update(task, advance=1)
                r.close()
                continue

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
                logging.info(
                    f"\nJOB DESCRIPTION NOT FOUND FOR URL {i + 1}: " + str(url) + "\n"
                )

            title = JOB_POSTING_TITLES[i].lower()
            jd_text_lower = JOB_DESCRIPTIONS_TEXT[-1].lower()
            JOB_IS_PHD.append("phd" in title or "phd" in jd_text_lower)

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
                logging.info(
                    f"\nJOB CRITERIA NOT FOUND FOR URL {i + 1}: " + str(url) + "\n"
                )

            # LOCATION
            location = "N/A"
            for p in soup.find_all("p"):
                if "Location(s):" in p.get_text():
                    parent = p.find_parent("div")
                    if parent:
                        loc_input = parent.find(
                            "input", class_="j-form-input__disabled-cat"
                        )
                        if loc_input:
                            location = loc_input.get("value", "N/A")
                    break

            if any(
                region in location
                for region in (
                    "England",
                    "Scotland",
                    "Wales",
                    "Northern Ireland",
                    "London",
                )
            ):
                LOCATION_DIV.append("UK")
            elif "Ireland" in location:
                LOCATION_DIV.append("IE")
            else:
                logging.info(
                    f"\nLOCATION NOT RECOGNISED for URL {i + 1}: {url}, APPENDED AS {location}\n"
                )
                LOCATION_DIV.append(str(location))

            discipline = "N/A"
            for p in soup.find_all("p"):
                if "Subject Area(s):" in p.get_text():
                    parent = p.find_parent("div")
                    if parent:
                        disc_input = parent.find("input", class_="parent-category")
                        if disc_input:
                            discipline = disc_input.get("value", "N/A")
                    break

            JOB_DISCIPLINE.append(discipline)

            progress.update(task, advance=1)
            r.close()

    # Remove skipped URLs so downstream list lengths stay consistent
    while None in JOB_POSTING_URLS:
        JOB_POSTING_URLS.remove(None)

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
        raw_salary = "N/A"
        hours = "N/A"
        contract = "N/A"
        date_posted = "N/A"
        date_closes = "N/A"

        if div == "N/A":
            # Fixed: was missing date_posted and date_closes appends before continue,
            # causing all downstream lists to be shorter and indexes to misalign.
            JOB_SALARY_STRING.append(raw_salary)
            JOB_SALARY_LOWER.append(salary_lower)
            JOB_SALARY_UPPER.append(salary_upper)
            JOB_HOURS.append(hours)
            JOB_CONTRACT.append(contract)
            JOB_DATE_POSTED.append(date_posted)
            JOB_DATE_CLOSES.append(date_closes)
            continue

        for row in div.find_all("tr"):
            th = row.find("th")
            td = row.find("td")

            if not th or not td:
                continue
            header = th.get_text(strip=True)
            value = td.get_text(separator=" ", strip=True)

            if header == "Salary:":
                raw_salary = " ".join(value.split())
                salary_lower, salary_upper = ps.parse_salary_bounds(raw_salary)
            elif header == "Hours:":
                hours = value
            elif header == "Contract Type:":
                contract = value
            elif header == "Placed On:":
                date_posted = parse_date(value)
            elif header == "Closes:" or header == "Expires:":
                date_closes = parse_date(value)

        # Fallback for PhD studentships: criteria table rarely has a Salary: row,
        # but the stipend amount is usually stated in the JD text.
        if raw_salary == "N/A" and i < len(JOB_DESCRIPTIONS_TEXT):
            jd_snippet, stipend_lower, stipend_upper = ps.parse_stipend_from_jd(
                JOB_DESCRIPTIONS_TEXT[i]
            )
            if jd_snippet:
                raw_salary = jd_snippet
                salary_lower = stipend_lower
                salary_upper = stipend_upper

        JOB_SALARY_STRING.append(raw_salary)
        JOB_SALARY_LOWER.append(salary_lower)
        JOB_SALARY_UPPER.append(salary_upper)
        JOB_HOURS.append(hours)
        JOB_CONTRACT.append(contract)
        JOB_DATE_POSTED.append(date_posted)
        JOB_DATE_CLOSES.append(date_closes)

    is_closed_role()
    extract_fte()

    logging.info(f"Extracted criteria for {len(JOB_CRITERIA_DIV)} jobs.")


# =================================================================================
# EXTRACT FTE VALUE FROM JOB DESCRIPTION TEXT
# =================================================================================


def extract_fte():
    pattern = re.compile(r"\d\.\d\s*FTE")
    for txt in JOB_DESCRIPTIONS_TEXT:
        if not txt or txt.strip() in ("N/A", ""):
            JOB_FTE_VALUE.append(None)
        else:
            match = pattern.search(txt)
            if match:
                JOB_FTE_VALUE.append(match.group())
            else:
                JOB_FTE_VALUE.append("1.0 FTE")


# =================================================================================
# Parse the date strings to YYYY-MM-DD and handle ordinal suffixes.
# =================================================================================


def parse_date(date_str):
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    try:
        return dt.strptime(cleaned, "%d %B %Y").strftime("%Y-%m-%d")
    except ValueError:
        logging.info(f"DATE PARSING FAILED FOR: {date_str}")
        return "N/A"


# =================================================================================
# Check if the job posting is closed.
# =================================================================================


def is_closed_role():
    for date in JOB_DATE_CLOSES:
        if date != "N/A":
            if dt.now() > dt.strptime(date, "%Y-%m-%d"):
                JOB_IS_CLOSED.append(True)
            else:
                JOB_IS_CLOSED.append(False)
        else:
            JOB_IS_CLOSED.append(False)


# =================================================================================
# EXPORT THE JOB DESCRIPTIONS TO JSON IN JD FOLDER.
# =================================================================================


def export_job_descriptions():
    global INPUT_PATH, INPUT_FILE
    logging.info("EXPORTING JOB DESCRIPTIONS...")
    logging.info("=" * 100)

    jobs = get_jobs_from_file()

    for i, job in enumerate(jobs):
        job["jd_text"] = (
            JOB_DESCRIPTIONS_TEXT[i] if i < len(JOB_DESCRIPTIONS_TEXT) else "N/A"
        )

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
        job["salary_text"] = (
            JOB_SALARY_STRING[i] if i < len(JOB_SALARY_STRING) else "N/A"
        )
        job["salary_lower"] = JOB_SALARY_LOWER[i] if i < len(JOB_SALARY_LOWER) else None
        job["salary_upper"] = JOB_SALARY_UPPER[i] if i < len(JOB_SALARY_UPPER) else None
        job["hours"] = JOB_HOURS[i] if i < len(JOB_HOURS) else "N/A"
        job["contract_type"] = JOB_CONTRACT[i] if i < len(JOB_CONTRACT) else "N/A"
        job["date_posted"] = JOB_DATE_POSTED[i] if i < len(JOB_DATE_POSTED) else "N/A"
        job["date_closes"] = JOB_DATE_CLOSES[i] if i < len(JOB_DATE_CLOSES) else "N/A"
        job["is_phd"] = JOB_IS_PHD[i] if i < len(JOB_IS_PHD) else False
        job["is_closed"] = JOB_IS_CLOSED[i] if i < len(JOB_IS_CLOSED) else False
        job["location"] = LOCATION_DIV[i] if i < len(LOCATION_DIV) else "N/A"
        job["fte"] = JOB_FTE_VALUE[i] if i < len(JOB_FTE_VALUE) else None
        job["discipline"] = JOB_DISCIPLINE[i] if i < len(JOB_DISCIPLINE) else "N/A"

    academic = [job for job in jobs if not job["is_phd"]]
    phd = [job for job in jobs if job["is_phd"]]

    fh.write_file("criteria", jobs)
    fh.write_file("criteria_academic", academic)
    fh.write_file("criteria_phd", phd)

    logging.info("=" * 100)
    logging.info(f"Saved {len(jobs)} total criteria.")
    logging.info(f"  Academic: {len(academic)}")
    logging.info(f"  PhD Studentships: {len(phd)}")
    logging.info(
        f"{JOB_IS_CLOSED.count(True)} closed roles out of {len(jobs)} identified."
    )
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
