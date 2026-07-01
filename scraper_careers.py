import requests
import logging
import os
import json
import math
from config import CP_HEADERS
import file_handling as fh
from datetime import datetime as dt

cp_base_url = "https://api.careersportal.ie/api/members/v1/jobs/external"

URLS = [
    f"{cp_base_url}/jobsie",  
    f"{cp_base_url}/irish"
]

JOB_ID = []
JOB_LINK = []
JOB_TITLE = []
JOB_CONTENT = []
JOB_CREATED = []
JOB_EXPIRED = []
JOB_SALARY = []
JOB_LOCATION = []
JOB_REGION = []
JOB_COUNTRY = []
JOB_DISCIPLINE = []
JOB_SUBDISCIPLINE = []
JOB_COMPANY_NAME = []

PARSED_JOBS = []


def build_request(url):
    session = requests.Session()
    session.headers.update(CP_HEADERS)

    resp = requests.get(url, headers=CP_HEADERS, params={"_format": "json"}, timeout=60)
    resp.raise_for_status()
 
    try:
        folder_end = ""

        if "jobsie" in url:
            folder_end = "jobsie"
        elif "irish":
            folder_end = "irish_jobs"

        data = resp.json()
        fh.write_file(f"raw_careers_{folder_end}", data)
    except ValueError as e:
        raise ValueError(f"Non-JSON response from {url} feed: {e}")
    
    return data.get("job", [])

def load_results_to_dict(data):
    for job in data:
        url = job["link"]
        title = job["title"]
        content = job["content"]
        created = job["created"]
        expires = job["expires"]
        salary_range = job["salary_range"]
        region = job["region"]
        country = job["country"]
        categories = job["categories"]
        company = job["company_name"]

        if url and url != "":
            if "?cid=Partner_Careersportal___3" in url:
                clean_url = url.replace("?cid=Partner_Careersportal___3", "")
                url = clean_url
            elif "?cid=Partner_Careersportal___1" in url:
                clean_url = url.replace("?cid=Partner_Careersportal___1", "")
                url = clean_url
            elif "?cid=Partner_CP___1" in url:
                clean_url = url.replace("?cid=Partner_CP___1", "")
                url = clean_url

        loc_string = ""
        locations = job.get("locations", {})
        if isinstance(locations, dict):
            loc_val = locations.get("location", "")
            if isinstance(loc_val, str):
                loc_string = loc_val.strip()
            else:
                loc_string = ""
        else:
            loc_string = ""

        if "Ireland" in country:
            country = "IE"
        
        if isinstance(categories, dict):
            discipline = categories.get("discipline", "")
            subdiscipline = categories.get("subdiscipline", "")
            # Ensure both are strings before any string ops
            if not isinstance(discipline, str):
                discipline = ""
            if not isinstance(subdiscipline, str):
                subdiscipline = ""
            if discipline.lower() == "no discipline":
                discipline = ""
            if subdiscipline.lower() == "no discipline":
                subdiscipline = ""
        else:
            discipline = ""
            subdiscipline = ""

        if not created or not isinstance(created, str):
            created = ""
        try:
            created = dt.strptime(created.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            created = ""
        
        if not expires or not isinstance(expires, str):
            expires = ""
        try:
            expires = dt.strptime(expires.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            expires = ""

        if salary_range and salary_range != "":
            try:
                flt_sal = float(salary_range)
                int_sal = math.floor(flt_sal)
                salary_range  = int_sal
            except:
                print("Salary not parseable")
                salary_range = salary_range
            


        JOB_LINK.append(url)
        JOB_TITLE.append(title)
        JOB_CONTENT.append(content)
        JOB_CREATED.append(created)
        JOB_EXPIRED.append(expires)
        JOB_SALARY.append(salary_range)
        JOB_LOCATION.append(loc_string)
        JOB_REGION.append(region)
        JOB_COUNTRY.append(country)  
        JOB_DISCIPLINE.append(discipline)
        JOB_SUBDISCIPLINE.append(subdiscipline)
        JOB_COMPANY_NAME.append(company)
       
        if title and url:
            PARSED_JOBS.append(
                {
                    "title": title,
                    "url": url,
                    "organisation": company,
                    "jd_text": content,
                    "salary_lower": salary_range,
                    "date_posted": created,
                    "date_closes": expires,
                    "location": country,
                    "discipline": discipline,
                    "subdiscipline": subdiscipline
                }
            )
        
    deduplicate()

def deduplicate():

    print("IN DEDUPLICATE...")

    print("JOBS INPUTTED: " + str(len(PARSED_JOBS)))
    seen = set()
    unique = []

    for job in PARSED_JOBS:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)

    PARSED_JOBS.clear()
    print("UNIQUE: " + str(len(unique)))
    PARSED_JOBS.extend(unique)
    print("Unique jobs after deduplication: " + str(len(PARSED_JOBS)))
    fh.write_file("criteria_careers", PARSED_JOBS)
    print("Saved " + str(len(PARSED_JOBS)) + " jobs...")
    combine_files()


def combine_files():
    academic_file = fh.get_most_recent_item("criteria")
    careers_file = fh.get_most_recent_item("criteria_careers")

    academic_path = os.path.join(os.path.join("data", "criteria"), academic_file)
    careers_path = os.path.join(os.path.join("data", "criteria_careers"), careers_file)

    if academic_file and careers_file:
        with open(academic_path, "r", encoding="utf-8") as f:
            academic = json.load(f)

        with open(careers_path, "r", encoding="utf-8") as f:
            careers = json.load(f)

        for record in academic:
            record["source"] = "jobs.ac.uk"

        for record in careers:
            record["source"] = "careersportal.ie"

        combined = academic + careers

        fh.write_file("combined_criteria", combined)

        print(f"Written {len(combined)} records")
        print(f"  Academic: {len(academic)}")
        print(f"  Careers:  {len(careers)}")

def init():
    jobs_ie_data = build_request(URLS[0])
    irishjobs_data = build_request(URLS[1])

    load_results_to_dict(jobs_ie_data)
    load_results_to_dict(irishjobs_data)