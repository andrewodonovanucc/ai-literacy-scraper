# =======================================================================================
# IMPORTS
# =======================================================================================

import requests
import time
import logging
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from rich.progress import Progress
from config import SEARCH_TERMS, REQUEST_DELAY
import json
import math
import os
import file_handling as fh

# =======================================================================================
# SEARCH PARAMETER VARIABLES
# =======================================================================================
BASE_URL = "https://www.jobs.ac.uk"
BASE_SEARCH_URL = BASE_URL + "/search/?keywords="

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
#   COUNTS THE OVERALL RESULTS FOR JOB LISTINGS
# =======================================================================================


def get_sum_total_results():
    for term in SEARCH_TERMS:
        global sum_total_results
        # Fetch first page to get total results
        first_url = BASE_SEARCH_URL + fix_url(term)
        r = requests.get(first_url)

        soup = bs(r.text, "html.parser")

        # Calculate how many results for each page
        total = get_total_results(soup)
        sum_total_results += total


# =======================================================================================
#   REPLACE SPACES WITH "+" SIGN IN THE URL
# =======================================================================================


def fix_url(url):
    url = url.replace(" ", "+")
    return url


# =======================================================================================
#   FETCH ALL RESULTS FROM EACH PAGE
# =======================================================================================


def fetch_all_pages():
    global sum_total_results

    get_sum_total_results()
    logging.info("OVERALL TOTAL RESULTS: " + str(sum_total_results))

    total_pages = math.ceil(sum_total_results / PAGE_SIZE)

    with Progress() as progress:
        task = progress.add_task("Fetching all jobs...", total=total_pages)

        for term in SEARCH_TERMS:
            logging.info("\nSearching: " + term)

            first_url = BASE_SEARCH_URL + fix_url(term)
            r = requests.get(first_url)
            time.sleep(REQUEST_DELAY)

            soup = bs(r.text, "html.parser")

            total = get_total_results(soup)
            logging.info("Total results for '" + term + "': " + str(total))

            jobs = soup.find_all("div", class_="j-search-result__result")
            FOUND_JOBS.extend(jobs)
            progress.update(task, advance=1)

            start_index = PAGE_SIZE
            while start_index < total:
                page_url = (
                    BASE_SEARCH_URL
                    + fix_url(term)
                    + "&SortOrder=0&pageSize="
                    + str(PAGE_SIZE)
                    + "&startIndex="
                    + str(start_index)
                )
                r = requests.get(page_url)
                # time.sleep(REQUEST_DELAY)

                soup = bs(r.text, "html.parser")
                jobs = soup.find_all("div", class_="j-search-result__result")
                FOUND_JOBS.extend(jobs)

                start_index += PAGE_SIZE
                progress.update(task, advance=1)


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


def init():
    fetch_all_pages()
    parse_jobs()
