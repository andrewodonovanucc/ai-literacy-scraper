# =================================================================================
# IMPORTS
# =================================================================================

import os
import datetime as dt
import time
import logging
import json

# ======================================================================================
#   MAKE A FILE WITH THE CURRENT DATE AND TIME
# ======================================================================================


def make_file(folder):
    os.makedirs(os.path.join("data", folder), exist_ok=True)
    filename = dt.datetime.now().strftime(f"{folder}-%Y%m%d-%H%M.json")
    filepath = os.path.join("data", folder, filename)
    return filepath


# ======================================================================================
# SAVE DATA TO JSON FILE
# ======================================================================================


def save_json(fp, data_array):
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data_array, f, indent=4, ensure_ascii=False)
    # logging.info("Saved " + str(len(data_array)) + ' jobs to "' + fp + '"')


# =================================================================================
# GET MOST RECENT ITEM
# =================================================================================


def get_most_recent_item(folder):
    most_recent_file_name = None
    most_recent_time = 0

    for item in os.scandir(os.path.join("data", folder)):
        if item.is_file():
            modified_time = item.stat().st_mtime_ns
            if modified_time > most_recent_time:
                most_recent_time = modified_time
                most_recent_file_name = item.name
    logging.info("=" * 100)
    logging.info("Most recent file name: " + most_recent_file_name)
    logging.info("Most recent file time: " + str(most_recent_time))
    logging.info("=" * 100)

    return most_recent_file_name


# =================================================================================
# WRITE DATA TO FILE
# =================================================================================


def write_file(folder, data_array):
    path = make_file(folder)
    save_json(path, data_array)
