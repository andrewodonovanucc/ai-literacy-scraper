import streamlit as st
from streamlit.web import cli as stcli
import sys
import pandas as pd
import file_handling as fh
import os
import json
import analyse
import logging

INPUT_FILE = None
INPUT_PATH = None

JOBS_FROM_JSON = []

# =================================================================================
# LOAD THE JOBS FROM THE MOST RECENT CRITERIA FILE
# =================================================================================

def get_jobs_from_file():
    global JOBS_FROM_JSON
    INPUT_FILE = fh.get_most_recent_item("filters")
    INPUT_PATH = os.path.join("data", "filters", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as json_file:
        JOBS_FROM_JSON = json.load(json_file)
    update_jobs_with_links()
    return JOBS_FROM_JSON

 # =================================================================================
# UPDATE THE JOBS WITH LINK MARKDOWN FOR STREAMLIT
# =================================================================================  

def update_jobs_with_links():
    global JOBS_FROM_JSON
    for job in JOBS_FROM_JSON:
        # print(job["url"])
        job["url"] = "[LINK](" + job["url"] + ")"
        # print(job["url"])

    fh.write_file("analyse", JOBS_FROM_JSON)


# =================================================================================
# LOAD THE UPDATED JOBS FROM JSON TO PANDAS
# =================================================================================

def read_json_to_pandas():
    INPUT_FILE = fh.get_most_recent_item("analyse")
    INPUT_PATH = os.path.join("data", "analyse", INPUT_FILE)
    logging.info("READING JSON FILE TO DATAFRAME...")
    jobs = pd.read_json(INPUT_PATH)
    jobs.drop(columns=["salary_text", "jd_text"], inplace=True)
    return jobs

# =================================================================================
# BUILD THE STREAMLIT APP PAGE
# =================================================================================

def build_page():
    st.set_page_config(layout="wide")
    st.title("AI Literacy Job Analysis")
    st.write("This dashboard provides insights into the AI literacy job market based on the latest scraped data.")
    data = analyse.read_json_to_pandas()
    st.dataframe(
        data,
        column_config={
            "url": st.column_config.LinkColumn("URL", display_text="View")
        },
        hide_index=True
    )

# =================================================================================
#  RUN EVERYTHING
# =================================================================================

def init():
    build_page()
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(stcli.main())
