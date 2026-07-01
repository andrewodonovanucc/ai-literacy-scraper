import statistics
import file_handling as fh
import os
import json
import logging

INPUT_FILE = None
INPUT_PATH = None

JOBS_FROM_JSON = []

# =================================================================================
# LOAD THE JOBS FROM THE MOST RECENT CRITERIA FILE
# =================================================================================

def get_jobs_from_file():
    global JOBS_FROM_JSON, INPUT_FILE, INPUT_PATH
    INPUT_FILE = fh.get_most_recent_item("combined_criteria")
    INPUT_PATH = os.path.join("data", "combined_criteria", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        combined_jobs = json.load(json_file)

    linkedin_jobs = []
    try:
        linkedin_file = fh.get_most_recent_item("criteria_linkedin")
    except Exception:
        linkedin_file = None

    if linkedin_file:
        linkedin_path = os.path.join("data", "criteria_linkedin", linkedin_file)
        with open(linkedin_path, encoding="utf-8") as f:
            linkedin_jobs = json.load(f)

    JOBS_FROM_JSON = combined_jobs + linkedin_jobs

    for job in JOBS_FROM_JSON:
        if job.get("discipline") == "N/A":
            job["discipline"] = None
        if "is_phd" not in job:
            job["is_phd"] = False
        if job.get("is_closed") in (None, "N/A"):
            job["is_closed"] = False
        if "institution" not in job:
            job["institution"] = job.get("organisation", "")

    return JOBS_FROM_JSON

# =======================================================================================
#   MENU TO SELECT SEARCH TERMS
# =======================================================================================
def menu():
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION TO ANALYSE:   ")
    logging.info("=" * 100)
    logging.info("  1. JUST ACADEMIC JOBS (jobs.ac.uk)")
    logging.info("  2. JUST PHD STUDENTSHIPS (jobs.ac.uk)")
    logging.info("  3. LINKEDIN JOBS")
    logging.info("  4. ALL")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt

# =======================================================================================
#   SELECT POSTING TYPE
# =======================================================================================

def select_posting_type(data, opt=None):
    if opt is None:
        opt = menu()
        while opt not in ("1", "2", "3", "4"):
            logging.info("PLEASE SELECT A VALID OPTION")
            opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("SELECTED TO ANALYSE ACADEMIC JOBS")
        return [job for job in data if job.get("source") == "jobs.ac.uk" and not job.get("is_phd")]
    elif opt == "2":
        logging.info("SELECTED TO ANALYSE PHD STUDENTSHIPS")
        return [job for job in data if job.get("source") == "jobs.ac.uk" and job.get("is_phd")]
    elif opt == "3":
        logging.info("SELECTED TO ANALYSE LINKEDIN JOBS")
        return [job for job in data if job.get("source") == "linkedin"]
    else:
        logging.info("SELECTED TO ANALYSE ALL")
        return data


# =================================================================================
# SORT / ANALYSE FUNCTIONS
# =================================================================================

def sort_by_ai_matches(data, descending=True):
    return sorted(data, key=lambda job: job.get("ai_matches", 0), reverse=descending)

def sort_by_salary(data, descending=True):
    return sorted(
        data,
        key=lambda job: (job["salary_lower"] if job.get("salary_lower") is not None else float("-inf")),
        reverse=descending,
    )

def salary_by_discipline(data):
    discipline_salaries = {}

    for job in data:
        disc = job.get("discipline") or "N/A"
        sal = job.get("salary_lower")

        if sal is None:
            continue
        if disc == "N/A":
            continue
        discipline_salaries.setdefault(disc, []).append(sal)

    results = {}
    for disc, salaries in discipline_salaries.items():
        try:
            mode = statistics.mode(salaries)
        except statistics.StatisticsError:
            mode = None
        results[disc] = {
            "n": len(salaries),
            "mean": round(statistics.mean(salaries)),
            "median": round(statistics.median(salaries)),
            "mode": round(mode) if mode is not None else "N/A",
        }
    return dict(sorted(results.items(), key=lambda x: -x[1]["mean"]))

def ai_matches_by_discipline(data):
    discipline_matches = {}

    for job in data:
        disc = job.get("discipline") or "N/A"
        matches = job.get("ai_matches", 0)
        discipline_matches.setdefault(disc, []).append(matches)

    results = {}
    for disc, match_list in discipline_matches.items():
        results[disc] = {
            "n": len(match_list),
            "total_matches": sum(match_list),
            "avg_matches": round(sum(match_list) / len(match_list), 2),
            "roles_with_ai": sum(1 for m in match_list if m > 0),
            "pct_with_ai": round(sum(1 for m in match_list if m > 0) / len(match_list) * 100, 1),
        }

    return dict(sorted(results.items(), key=lambda x: -x[1]["total_matches"]))

def output_salary(jobs):
    sorted_jobs = sort_by_salary(jobs)
    for job in sorted_jobs:
        if job.get("salary_lower") is not None and job["salary_lower"] > 10000:
            logging.info(f"{job['salary_lower']:>10} EUR | {job['title']}")

def output_ai_match(jobs):
    sorted_jobs = sort_by_ai_matches(jobs)
    for job in sorted_jobs:
        if job.get("ai_matches", 0) > 2:
            logging.info(f"{job['ai_matches']:>3} matches | {job['title']}")

def init(analyse_type=None):
    jobs = get_jobs_from_file()
    jobs = select_posting_type(jobs, analyse_type)

    logging.info("=" * 100)
    discipline_stats = salary_by_discipline(jobs)
    logging.info("=" * 100)
    logging.info("SALARY BY DISCIPLINE (EUR, salary_lower, 10k-200k only):")
    logging.info(f"{'Discipline':<45} {'N':>5} {'Mean':>10} {'Median':>10} {'Mode':>10}")
    logging.info("-" * 85)
    for disc, stats in discipline_stats.items():
        if stats["n"] > 3:
            logging.info(
                f"{disc:<45} {stats['n']:>5} {stats['mean']:>10,} {stats['median']:>10,} {str(stats['mode']):>10}"
            )
    logging.info("=" * 100)

    ai_stats = ai_matches_by_discipline(jobs)
    logging.info("=" * 100)
    logging.info("AI MATCHES BY DISCIPLINE:")
    logging.info(f"{'Discipline':<45} {'N':>5} {'Total':>7} {'Avg':>7} {'w/ AI':>7} {'%':>7}")
    logging.info("-" * 85)
    for disc, stats in ai_stats.items():
        if stats["n"] > 3:
            logging.info(
                f"{disc:<45} {stats['n']:>5} {stats['total_matches']:>7} "
                f"{stats['avg_matches']:>7.2f} {stats['roles_with_ai']:>7} {stats['pct_with_ai']:>6.1f}%"
            )
    logging.info("=" * 100)