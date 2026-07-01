from dotenv import load_dotenv
import os
import re

load_dotenv()
# print("COOKIE LOADED:", bool(os.environ.get('LI_AT_COOKIE')))

import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, \
    ExperienceLevelFilters, OnSiteOrRemoteFilters, SalaryBaseFilters


from config import INDUSTRY_SEARCH_TERMS
import file_handling as fh

def clean_url(url):
    url_parts = url.split("?")
    new_url = url_parts[0]
    return new_url

logging.basicConfig(level=logging.INFO)

QUERIES = []
# JOB_TITLES = []
# JOB_ORG = []
# JOB_URL = []
# JOB_DESC = []
# JOB_LOCATION = []
PARSED_JOBS = []


# Fired once for each successfully processed job
def on_data(data: EventData):
    cleaned_url = clean_url(str(data.link))
  #  print('[ON_DATA]', f"TITLE: {data.title}\nCOMPANY: {data.company}\nURL: {cleaned_url}\nDATE: {data.date}\nDATE TEXT: {data.date_text}\nLOCATION: {data.location}\nSKILLS: {data.skills}")
    # JOB_TITLES.append(data.title)
    # JOB_ORG.append(data.company)
    # JOB_URL.append(cleaned_url)
    # JOB_DESC.append(data.description)
    # JOB_LOCATION.append(data.location)
    PARSED_JOBS.append({
        "title": data.title,
        "url": cleaned_url,
        "organisation": data.company,
        "jd_text": data.description,
        "location": data.location,
        "source": "LinkedIn"
    })
    

# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


def build_scraper():
    print("BUILDING SCRAPER...")
    scraper = LinkedinScraper(
        chrome_executable_path=os.environ.get('CHROME_DR'),  # path to chromedriver.exe
        chrome_binary_location=os.environ.get('CHROME_BIN'),  # path to chrome.exe
        chrome_options=None,  # Custom Chrome options here
        headless=False,  # Overrides headless mode only if chrome_options is None
        max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
        slow_mo=1.5,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
        page_load_timeout=40  # Page load timeout (in seconds)    
    )

    print("ADDING EVENT LISTENERS...")
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)
    print("SCRAPER BUILT...")
    return scraper


def build_queries():
    for role in INDUSTRY_SEARCH_TERMS:
        QUERIES.append(
            Query(
                query=role,
                options=QueryOptions(
                    locations=["Ireland", "UK", "European Union"],
                    apply_link=False,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
                    skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
                    # page_offset=0,  # How many pages to skip
                    limit=1000,
                    filters=QueryFilters(       
                        relevance=RelevanceFilters.RELEVANT,
                        time=TimeFilters.MONTH,
                        type=[TypeFilters.FULL_TIME],
                        # experience=[ExperienceLevelFilters.MID_SENIOR],
                        base_salary=SalaryBaseFilters.SALARY_40K
                    )
                )
            )
        )


def init():
    li_scraper = build_scraper()
    build_queries()
    li_scraper.run(QUERIES)
    print("WRITING TO FILE...")
    fh.write_file("jobs_linkedin", PARSED_JOBS)