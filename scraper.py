# =======================================================================================
# IMPORTS
# =======================================================================================

import requests
import time
import logging
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from rich.progress import Progress
from config import (
    JOB_SEARCH_TERMS,
    PHD_SEARCH_TERMS,
    COMBINED_SEARCH_TERMS,
    REQUEST_DELAY,
    LOCATIONS,
    HEADERS,
)
import json
import math
import os
import file_handling as fh
import helper as hp

# =======================================================================================
# SEARCH PARAMETER VARIABLES
# =======================================================================================
BASE_URL = "https://www.jobs.ac.uk"
BASE_SEARCH_URL = BASE_URL + "/search/?keywords="

INDEED_URL = "https://www.jobs.ie/jobs"

PAGE_SIZE = 25
URLS = []

# =======================================================================================
#   ARRAY CONTAINERS
# =======================================================================================

COMPLETED_REQUESTS = []
PRETTIFIED_SOUPS = []
FOUND_JOBS = []
PARSED_JOBS = []

# =======================================================================================
#   GLOBAL COUNTER VARIABLE TO TRACK THE OVERALL TOTAL RESULTS
# =======================================================================================

sum_total_results = 0


# =======================================================================================
#   MENU TO SELECT SEARCH TERMS
# =======================================================================================
def menu():
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION:   ")
    logging.info("=" * 100)
    logging.info("  1. JUST ACADEMIC JOBS")
    logging.info("  2. JUST PHD STUDENTSHIPS")
    logging.info("  3. BOTH")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt


# =======================================================================================
#   SELECT SEARCH TERM LIST YOU WANT TO USE
# =======================================================================================


def select_terms_list(opt=None):
    if opt is None:
        opt = menu()
        while opt not in ("1", "2", "3"):
            logging.info("PLEASE SELECT A VALID OPTION")
            opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("Chose to Search Jobs.")
        return JOB_SEARCH_TERMS
    elif opt == "2":
        logging.info("Chose to Search PhD Studentships.")
        return PHD_SEARCH_TERMS
    else:
        logging.info("Chose to Search Jobs and PhD Studentships.")
        return COMBINED_SEARCH_TERMS


# =======================================================================================
#   COUNTS THE TOTAL RESULTS PER SEARCH TERM (25/PAGE)
# =======================================================================================


def get_total_results(soup):
    result_count = soup.find("strong", class_="job-count")
    if result_count:
        text = result_count.text.strip()
        total = int(text)
        return total
    return 0


# =======================================================================================
#   REPLACE SPACES WITH "+" SIGN IN THE URL
# =======================================================================================


def fix_url(url):
    url = url.replace(" ", "+")
    return url


# =======================================================================================
#   BUILD SEARCH URL FOR A GIVEN TERM AND LOCATION
# =======================================================================================


def build_search_url(term, country_code, country_name):
    location_param = f"&country%5B%5D={fix_url(country_name)}&country%5B%5D={country_code}&location={fix_url(country_name)}"
    return BASE_SEARCH_URL + fix_url(term) + location_param + f"&_={int(time.time())}"


# =======================================================================================
#   COUNTS THE OVERALL RESULTS FOR JOB LISTINGS
# =======================================================================================


def get_sum_total_results(session, stl):
    global sum_total_results

    for term in stl:
        for code, name in LOCATIONS.items():
            url = build_search_url(term, code, name)
            r = session.get(url, timeout=60)
            soup = bs(r.text, "html.parser")
            result_count = soup.find("strong", class_="job-count")
            if not result_count:
                logging.info("REQUEST HEADERS: " + str(r.headers))
            total = get_total_results(soup)
            # logging.info(f"\nTotal for '{term}' in {name}: {total}")
            sum_total_results += total
            r.close()


# =======================================================================================
#   FETCH ALL RESULTS FROM EACH PAGE
# =======================================================================================


def fetch_all_pages(opt=None):
    global sum_total_results

    stl = select_terms_list(opt)

    session = requests.Session()
    session.headers.update(HEADERS)

    get_sum_total_results(session, stl)
    logging.info("OVERALL TOTAL RESULTS: " + str(sum_total_results))

    total_pages = math.ceil(sum_total_results / PAGE_SIZE)

    with Progress() as progress:
        task = progress.add_task("Fetching all jobs...", total=total_pages)

        for term in stl:
            for code, name in LOCATIONS.items():
                url = build_search_url(term, code, name)
                r = hp.request_page(session, url, label=f"'{term}' in {name}")
                if r is None:
                    progress.update(task, advance=1)
                    continue
                soup = bs(r.text, "html.parser")
                total = get_total_results(soup)
                logging.info(f"\nSearching: {term} | {code} | Total: {total}")
                jobs = soup.find_all("div", class_="j-search-result__result")
                FOUND_JOBS.extend(jobs)
                progress.update(task, advance=1)
                r.close()

                start_index = PAGE_SIZE
                while start_index < total:
                    page_url = (
                        build_search_url(term, code, name)
                        + "&SortOrder=0&pageSize="
                        + str(PAGE_SIZE)
                        + "&startIndex="
                        + str(start_index)
                    )
                    r = hp.request_page(
                        session,
                        page_url,
                        label=f"'{term}' page {start_index // PAGE_SIZE + 1}",
                    )
                    if r is None:
                        start_index += PAGE_SIZE
                        progress.update(task, advance=1)
                        continue
                    soup = bs(r.text, "html.parser")
                    jobs = soup.find_all("div", class_="j-search-result__result")
                    FOUND_JOBS.extend(jobs)
                    start_index += PAGE_SIZE
                    progress.update(task, advance=1)
                    r.close()


# =======================================================================================
#   PUT JOBS IN DICT FORMAT TO BE USED TO WRITE JSON
# =======================================================================================


def parse_jobs():
    for job in FOUND_JOBS:
        title, url, dept, institution = None, None, None, None

        title_div = job.find("div", class_="j-search-result__text")
        if title_div:
            link = title_div.find("a")
            if link:
                title = link.text.strip()
                url = BASE_URL + link.get("href")

        dept_div = job.find("div", class_="j-search-result__department")
        if dept_div:
            dept = dept_div.text.strip()

        ins_div = job.find("div", class_="j-search-result__employer")
        if ins_div:
            bold = ins_div.find("b")
            if bold:
                institution = bold.text.strip()

        if title and url:
            PARSED_JOBS.append(
                {
                    "title": title,
                    "url": url,
                    "department": dept,
                    "institution": institution,
                }
            )

    deduplicate()


# =======================================================================================
#   REMOVE DUPLICATE JOBS ON UNIQUE JOB POSTING URL
# =======================================================================================


def deduplicate():

    logging.info("IN DEDUPLICATE...")

    logging.info("JOBS INPUTTED: " + str(len(PARSED_JOBS)))
    seen = set()
    unique = []

    for job in PARSED_JOBS:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)

    PARSED_JOBS.clear()
    logging.info("UNIQUE: " + str(len(unique)))
    PARSED_JOBS.extend(unique)
    logging.info("Unique jobs after deduplication: " + str(len(PARSED_JOBS)))
    fh.write_file("jobs", PARSED_JOBS)
    logging.info("Saved " + str(len(PARSED_JOBS)) + " jobs...")


# =======================================================================================
#   RUN EVERYTHING
# =======================================================================================


def init(scrape_type=None):
    fetch_all_pages(scrape_type)
    parse_jobs()
