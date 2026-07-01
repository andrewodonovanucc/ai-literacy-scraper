import os
import json
import file_handling as fh
from config import AI_TERMS
import re
from rich.progress import Progress
import logging

JOB_DESCRIPTIONS = []
JOB_DESCRIPTIONS_LOWER = []
AI_PATTERNS = []

MATCHED = []
UNMATCHED = []
AI_MATCHES = {}

ALL_JOBS = []


def load_combined_and_linkedin():
    combined_filename = fh.get_most_recent_item("combined_criteria")
    combined_filepath = os.path.join("data", "combined_criteria", combined_filename)
    with open(combined_filepath, encoding="utf-8") as f:
        combined_data = json.load(f)

    linkedin_data = []
    try:
        linkedin_filename = fh.get_most_recent_item("criteria_linkedin")
    except Exception:
        linkedin_filename = None

    if linkedin_filename:
        linkedin_filepath = os.path.join("data", "criteria_linkedin", linkedin_filename)
        with open(linkedin_filepath, encoding="utf-8") as f:
            linkedin_data = json.load(f)

    return combined_data + linkedin_data


# =================================================================================
#   READ JOB DESCRIPTIONS FROM COMBINED CRITERIA ONLY
# =================================================================================


def read_job_descs():
    global ALL_JOBS
    ALL_JOBS = load_combined_and_linkedin()

    for jd in ALL_JOBS:
        text = str(jd.get("jd_text") or "")
        JOB_DESCRIPTIONS.append(text)
        JOB_DESCRIPTIONS_LOWER.append(text.lower())


# =================================================================================
#   MAKE THE REGEX PATTERN
# =================================================================================


def make_regex():
    for term in AI_TERMS:
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        AI_PATTERNS.append((term, pattern))


# =================================================================================
#   CHECK JOB DESCRIPTION FOR AI TERMS
# =================================================================================


def check_jd_for_ai_terms(text):
    found = []
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for term, pattern in AI_PATTERNS:
        for sentence in sentences:
            if pattern.search(sentence):
                found.append({"term": term, "sentence": sentence.strip()})
    return found


def scan_all_jds():
    total = len(JOB_DESCRIPTIONS_LOWER)

    with Progress() as progress:
        task = progress.add_task("Performing AI Search...", total=total)
        for i, text in enumerate(JOB_DESCRIPTIONS_LOWER):
            found = check_jd_for_ai_terms(text)
            AI_MATCHES[i] = {"matches": found}
            if found:
                MATCHED.append(i)
            else:
                UNMATCHED.append(i)
            progress.update(task, advance=1)


def export_with_ai_matches():
    logging.info("MATCHED: " + str(len(MATCHED)))
    logging.info("UNMATCHED: " + str(len(UNMATCHED)))
    logging.info("=" * 100)
    logging.info("EXPORT...")

    for i, job in enumerate(ALL_JOBS):
        match_data = AI_MATCHES.get(i, {})
        matches = match_data.get("matches", [])
        job["ai_matches"] = len(matches)
        job["ai_sentences"] = [m["sentence"] for m in matches]

    fh.write_file("filters", ALL_JOBS)
    logging.info("Exported to filters")


def init():
    read_job_descs()
    make_regex()
    logging.info("JOB DESCRIPTIONS READ....")
    scan_all_jds()
    export_with_ai_matches()
