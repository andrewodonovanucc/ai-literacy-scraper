import file_handling as fh
import config
import json
import requests
from rich.progress import Progress
from bs4 import BeautifulSoup as bs
import os
import logging

INPUT_FILE = None

JOB_POSTING_URLS = []
JOB_CRITERIA_DIV = []
JOB_CRITERIA_p = []


def read_json_to_dict(file):
    logging.info("READING JSON FILE TO DICTIONARY...")
    INPUT_PATH = os.path.join("data", "jobs", file)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        data = json.load(json_file)

    for item in data:
        JOB_POSTING_URLS.append(item["url"])


def get_job_criteria():
    logging.info("=" * 100)
    logging.info("GETTING JOB CRITERIA...")

    total = len(JOB_POSTING_URLS)
    logging.info("TOTAL POTENTIAL JOB CRITERIA: " + str(total))
    logging.info("=" * 100)

    with Progress() as progress:
        task = progress.add_task("Fetching job criteria...", total=total)
        for i, url in enumerate(JOB_POSTING_URLS):
            r = requests.get(url, timeout=60, headers=config.HEADERS)
            if r.status_code != 200:
                logging.info("Request failed")
            soup = bs(r.text, "html.parser")

            job_criteria_div = soup.find("div", class_="j-advert-details__container row-5")
            job_criteria_div = soup.find("div", class_="j-advert-details__container")

            if job_criteria_div:
                text = job_criteria_div.get_text(separator=" ", strip=True)
                JOB_CRITERIA_p.append(text)
            else:
                JOB_CRITERIA_p.append("N/A")
                logging.info(f"JOB CRITERIA NOT FOUND FOR URL {i + 1}: " + str(url))

            progress.update(task, advance=1)
            r.close()
            # time.sleep(config.REQUEST_DELAY)


def init():
    INPUT_FILE = fh.get_most_recent_item("jobs")
    read_json_to_dict(INPUT_FILE)
    get_job_criteria()
    for p in JOB_CRITERIA_p:
        logging.info(p)
