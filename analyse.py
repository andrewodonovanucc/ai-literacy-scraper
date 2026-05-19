import file_handling as fh
import os
import json

JOBS = []


def read_ai_jobs():
    filename = fh.get_most_recent_item("filters")
    filepath = os.path.join("data", "filters", filename)
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    for job in data:
        JOBS.append(job)

def sort_by_ai_matches(data, descending=True):
    return sorted(data, key=lambda job: job["ai_matches"], reverse=descending)

def init():
    read_ai_jobs()
    sorted_jobs = sort_by_ai_matches(JOBS)
    for job in sorted_jobs:
        if job['ai_matches'] > 2:
            print(f"{job['ai_matches']:>3} matches | {job['title']}")

