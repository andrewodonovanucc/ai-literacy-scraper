import requests
import time
from bs4 import BeautifulSoup as bs
from config import SEARCH_TERMS, REQUEST_DELAY
import json


BASE_URL = "https://www.jobs.ac.uk"
BASE_SEARCH_URL = BASE_URL + "/search/?activeFacet=&resetFacet=&placeId=&keywords="
PAGE_SIZE = 25
URLS = []
COMPLETED_REQUESTS = []
PRETTIFIED_SOUPS = []
FOUND_JOBS = []
PARSED_JOBS = []

def parse_jobs():
    for job in FOUND_JOBS:
        title, url, dept, institution = None, None, None, None

        title_div = job.find('div', class_='j-search-result__text')
        if title_div:
            link = title_div.find('a')
            if link:
                title = link.text.strip()
                url = BASE_URL + link.get('href')

        dept_div = job.find('div', class_='j-search-result__department')
        if dept_div:
            dept = dept_div.text.strip()

        ins_div = job.find('div', class_='j-search-result__employer')
        if ins_div:
            bold = ins_div.find('b')
            if bold:
                institution = bold.text.strip()

        if title and url:
            PARSED_JOBS.append({
                "title":       title,
                "url":         url,
                "department":  dept,
                "institution": institution,
            })

    deduplicate()

def deduplicate():
    seen = set()
    unique = []
    for job in PARSED_JOBS:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)
    PARSED_JOBS.clear()
    PARSED_JOBS.extend(unique)
    print("Unique jobs after deduplication: " + str(len(PARSED_JOBS)))
    save_json()

def save_json():
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(PARSED_JOBS, f, indent=4, ensure_ascii=False)
    print("Saved " + str(len(PARSED_JOBS)) + " jobs to jobs.json")

def get_jobs():
    fetch_all_pages()
    parse_jobs()


def create_soup():
    for html in COMPLETED_REQUESTS:
        soup = bs(html, 'html.parser')
        jobs = soup.find_all('div', class_='j-search-result__result')
        if len(jobs) > 0:
            FOUND_JOBS.extend(jobs)


def fix_url(url):
    url = url.replace(" ", "+")
    return url

def get_total_results(soup):
    result_count = soup.find('strong', class_='job-count')
    if result_count:
        text = result_count.text.strip()
        # extract just the number e.g. "143" from "1-25 of 143 jobs"
        total = int(text)
        return total
    return 0

def fetch_all_pages():
    for term in SEARCH_TERMS:
        print("\nSearching: " + term)
        start_index = 0

        # Fetch first page to get total results
        first_url = BASE_SEARCH_URL + '"' + fix_url(term) + '"' + "&location=&startIndex=0&pageSize=" + str(PAGE_SIZE)
        r = requests.get(first_url)
        time.sleep(REQUEST_DELAY)

        soup = bs(r.text, 'html.parser')
        total = get_total_results(soup)
        print("Total results: " + str(total))

        # Parse first page immediately
        jobs = soup.find_all('div', class_='j-search-result__result')
        FOUND_JOBS.extend(jobs)

        # Calculate remaining pages
        start_index = PAGE_SIZE
        while start_index < total:
            page_url = BASE_SEARCH_URL + '"' + fix_url(term) + '"' + "&location=&startIndex=" + str(start_index) + "&pageSize=" + str(PAGE_SIZE)
            r = requests.get(page_url)
            time.sleep(REQUEST_DELAY)

            soup = bs(r.text, 'html.parser')
            jobs = soup.find_all('div', class_='j-search-result__result')
            FOUND_JOBS.extend(jobs)

            start_index += PAGE_SIZE

def init():
    get_jobs()

   
init()