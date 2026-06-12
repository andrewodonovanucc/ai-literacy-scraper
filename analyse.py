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
    INPUT_FILE = fh.get_most_recent_item("filters")
    INPUT_PATH = os.path.join("data", "filters", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        JOBS_FROM_JSON = json.load(json_file)
    return JOBS_FROM_JSON


# =======================================================================================
#   MENU TO SELECT SEARCH TERMS
# =======================================================================================
def menu():    
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION TO ANALYSE:   ")
    logging.info("=" * 100)
    logging.info("  1. JUST ACADEMIC JOBS")
    logging.info("  2. JUST PHD STUDENTSHIPS")
    logging.info("  3. BOTH")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt

# =======================================================================================
#   SELECT POSTING TYPE (JOB OR PHD STUDENTSHIP OR BOTH)
# =======================================================================================

def select_posting_type(data):
    opt = menu()
    while opt not in ("1", "2", "3"):
        logging.info("PLEASE SELECT A VALID OPTION")
        opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("SELECTED TO ANALYSE JOBS")
        return [job for job in data if not job.get("is_phd")]
    elif opt == "2":
        logging.info("SELECTED TO ANALYSE PHD STUDENTSHIPS")
        return [job for job in data if job.get("is_phd")]
    else:
        logging.info("SELECTED TO ANALYSE BOTH")
        return data
    
# =================================================================================
# SORT / ANALYSE FUNCTIONS
# =================================================================================

def sort_by_ai_matches(data, descending=True):
    return sorted(data, key=lambda job: job["ai_matches"], reverse=descending)

def sort_by_salary(data, descending=True):
    return sorted(data, key=lambda job: (job["salary_lower"] if job["salary_lower"] is not None else float('-inf')), reverse=descending)

def salary_by_discipline(data):
    discipline_salaries = {}

    for job in data:
        disc = job.get("discipline") or "N/A"
        sal = job.get("salary_lower")
        is_phd = job.get("is_phd")

        # Disregard entries where salary is None
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
        if job['salary_lower'] is not None and job['salary_lower'] > 10000:
            logging.info(f"{job['salary_lower']:>10} EUR | {job['title']}")


def output_ai_match(jobs):
    sorted_jobs = sort_by_ai_matches(jobs)
    for job in sorted_jobs:
        if job['ai_matches'] > 2:
            logging.info(f"{job['ai_matches']:>3} matches | {job['title']}")

def init():
    jobs = get_jobs_from_file()
    jobs = select_posting_type(jobs)

    logging.info("=" * 100)
    discipline_stats = salary_by_discipline(jobs)
    logging.info("=" * 100)
    logging.info("SALARY BY DISCIPLINE (EUR, salary_lower, 10k-200k only):")
    logging.info(f"{'Discipline':<45} {'N':>5} {'Mean':>10} {'Median':>10} {'Mode':>10}")
    logging.info("-" * 85)
    for disc, stats in discipline_stats.items():
        if stats['n'] > 3:
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
        if stats['n'] > 3:
            logging.info(
                f"{disc:<45} {stats['n']:>5} {stats['total_matches']:>7} "
                f"{stats['avg_matches']:>7.2f} {stats['roles_with_ai']:>7} {stats['pct_with_ai']:>6.1f}%"
            )
    logging.info("=" * 100)