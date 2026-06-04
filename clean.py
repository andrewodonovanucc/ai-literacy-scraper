# import logging

# # =================================================================================
# # VARIABLES FOR FILE HANDLING
# # =================================================================================


# INPUT_FILE = None
# INPUT_PATH = None

# # =================================================================================
# # ARRAY CONTAINERS
# # =================================================================================

# # =================================================================================
# # LOAD THE LIST OF URLS TO BE SCRAPED
# # =================================================================================


# def read_json_to_dict():
#     logging.info("READING JSON FILE TO DICTIONARY...")
#     jobs = get_jobs_from_file()

#     for item in jobs:
#         JOB_POSTING_URLS.append(item["url"])


# # =================================================================================
# # READ THE JOBS FROM THE JSON FILE IN THE JOBS FOLDER
# # =================================================================================


# def get_jobs_from_file():
#     global INPUT_FILE, INPUT_PATH
#     INPUT_PATH = os.path.join("data", "jobs", INPUT_FILE)
#     with open(INPUT_PATH, encoding="utf-8") as json_file:
#         jobs = json.load(json_file)
#     return jobs
