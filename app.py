import streamlit as st
import pandas as pd
import file_handling as fh
import os

st.title("AI Literacy Job Analysis")
st.write("This dashboard provides insights into the AI literacy job market based on the latest scraped data.")
INPUT_FILE = fh.get_most_recent_item("criteria")
INPUT_PATH = os.path.join("data", "criteria", INPUT_FILE)
data =  pd.read_json(INPUT_PATH)
data.drop(columns=["salary_text", "jd_text"], inplace=True)
st.write(data)
