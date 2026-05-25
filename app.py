from altair.datasets import data
import streamlit as st
import pandas as pd
import file_handling as fh
import os
import analyse

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