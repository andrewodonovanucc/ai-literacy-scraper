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

# =================================================================================
#   READ JOB DESCRIPTIONS
# =================================================================================


def read_job_descs():
    filename = fh.get_most_recent_item("jd")
    filepath = os.path.join("data", "jd", filename)
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    for jd in data:
        jd_lower = str(jd["paragraph"])
        jd_lower = jd_lower.lower()

        JOB_DESCRIPTIONS_LOWER.append(jd_lower)
        JOB_DESCRIPTIONS.append(jd["paragraph"])


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
    total = len(JOB_DESCRIPTIONS)

    with Progress() as progress:
        task = progress.add_task("Performing AI Search...", total=total)
        for i, text in enumerate(JOB_DESCRIPTIONS_LOWER):
            found = check_jd_for_ai_terms(text)
            AI_MATCHES[i] = {"sentences": text, "matches": found}
            if found:
                MATCHED.append({"index": i, "sentences": text, "matches": found})
            else:
                UNMATCHED.append({"index": i, "text": text})

            progress.update(task, advance=1)


def export_with_ai_matches():
    logging.info("MATCHED: " + str(len(MATCHED)))
    logging.info("UNMATCHED: " + str(len(UNMATCHED)))
    logging.info("=" * 100)
    logging.info("EXPORT...")
    file = fh.get_most_recent_item("jobs")
    filepath = os.path.join("data", "jobs", file)

    with open(filepath, encoding="utf-8") as f:
        jobs = json.load(f)

    for i, job in enumerate(jobs):
        match_data = AI_MATCHES.get(i)
        job["ai_matches"] = len(match_data["matches"]) if match_data else 0

    fh.write_file("filters", jobs)
    logging.info(f"Exported to filters")


def init():
    read_job_descs()
    make_regex()
    logging.info("JOB DESCRIPTIONS READ....")
    scan_all_jds()

    export_with_ai_matches()
