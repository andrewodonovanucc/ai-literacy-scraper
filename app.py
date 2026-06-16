import streamlit as st
import pandas as pd
import plotly.express as px
import file_handling as fh
import os
import json
import analyse
import logging

# =================================================================================
# LOAD AND PREPARE DATA
# =================================================================================

@st.cache_data
def load_jobs():
    INPUT_FILE = fh.get_most_recent_item("filters")
    INPUT_PATH = os.path.join("data", "filters", INPUT_FILE)
    with open(INPUT_PATH, encoding="utf-8") as f:
        jobs = json.load(f)
    # Normalise "N/A" discipline to None (consistent with analyse.py)
    for job in jobs:
        if job.get("discipline") == "N/A":
            job["discipline"] = None
    return jobs


def filter_by_type(jobs, opt):
    if opt == "Academic Jobs":
        return [j for j in jobs if not j.get("is_phd")]
    elif opt == "PhD Studentships":
        return [j for j in jobs if j.get("is_phd")]
    return jobs


def jobs_to_df(jobs):
    df = pd.DataFrame(jobs)
    drop_cols = [c for c in ["jd_text", "salary_text", "ai_sentences"] if c in df.columns]
    df.drop(columns=drop_cols, inplace=True)
    return df


# =================================================================================
# CHART HELPERS
# =================================================================================

def salary_chart(jobs):
    stats = analyse.salary_by_discipline(jobs)
    # Only disciplines with n > 3
    rows = [
        {"Discipline": disc, "Mean (EUR)": s["mean"], "Median (EUR)": s["median"], "N": s["n"]}
        for disc, s in stats.items() if s["n"] > 3
    ]
    if not rows:
        st.info("Not enough data to display salary chart.")
        return
    df = pd.DataFrame(rows).set_index("Discipline")
    st.bar_chart(df[["Mean (EUR)", "Median (EUR)"]], horizontal=True)


def ai_chart(jobs):
    stats = analyse.ai_matches_by_discipline(jobs)
    rows = [
        {
            "Discipline": disc,
            "Total AI Matches": s["total_matches"],
            "% Roles with AI": s["pct_with_ai"],
            "N": s["n"],
        }
        for disc, s in stats.items()
        if s["n"] > 3 and disc != "N/A"
    ]
    if not rows:
        st.info("Not enough data to display AI matches chart.")
        return
    df = pd.DataFrame(rows).set_index("Discipline")
    st.bar_chart(df[["Total AI Matches"]], horizontal=True)


def ai_pie_charts(jobs):
    stats = analyse.ai_matches_by_discipline(jobs)
    disciplines = [
        (disc, s) for disc, s in stats.items()
        if s["n"] > 3 and disc != "N/A"
    ]
    if not disciplines:
        st.info("Not enough data to display pie charts.")
        return

    cols = st.columns(3)
    for i, (disc, s) in enumerate(disciplines):
        with_ai = s["roles_with_ai"]
        without_ai = s["n"] - s["roles_with_ai"]
        fig = px.pie(
            names=["With AI", "Without AI"],
            values=[with_ai, without_ai],
            title=f"{disc} (n={s['n']})",
            color_discrete_sequence=["#4C72B0", "#D3D3D3"],
            hole=0.3,
        )
        fig.update_traces(textinfo="percent", hovertemplate="%{label}: %{value} roles")
        fig.update_layout(
            margin=dict(t=40, b=10, l=10, r=10),
            showlegend=False,
            title_font_size=12,
            height=250,
        )
        cols[i % 3].plotly_chart(fig, use_container_width=True)


# =================================================================================
# TABLE HELPERS
# =================================================================================

def salary_table(jobs):
    stats = analyse.salary_by_discipline(jobs)
    rows = [
        {
            "Discipline": disc,
            "N": s["n"],
            "Mean (EUR)": f"{s['mean']:,}",
            "Median (EUR)": f"{s['median']:,}",
            "Mode (EUR)": str(s["mode"]),
        }
        for disc, s in stats.items() if s["n"] > 3
    ]
    if not rows:
        st.info("Not enough salary data.")
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def ai_table(jobs):
    stats = analyse.ai_matches_by_discipline(jobs)
    rows = [
        {
            "Discipline": disc,
            "N": s["n"],
            "Total Matches": s["total_matches"],
            "Avg Matches": s["avg_matches"],
            "Roles w/ AI": s["roles_with_ai"],
            "% w/ AI": f"{s['pct_with_ai']}%",
        }
        for disc, s in stats.items()
        if s["n"] > 3 and disc != "N/A"
    ]
    if not rows:
        st.info("Not enough AI match data.")
        return
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


# =================================================================================
# PAGE
# =================================================================================

def build_page():
    st.set_page_config(layout="wide", page_title="AI Literacy Job Analysis")
    st.title("AI Literacy in Academic Job Postings")

    jobs = load_jobs()

    # Sidebar filter
    with st.sidebar:
        st.header("Filter")
        posting_type = st.radio(
            "Posting type",
            ["Academic Jobs", "PhD Studentships", "Both"],
            index=0,
        )

    filtered = filter_by_type(jobs, posting_type)
    st.caption(f"Showing **{len(filtered)}** postings ({posting_type})")

    tab_salary, tab_ai, tab_jobs = st.tabs(["Salary by Discipline", "AI Matches by Discipline", "All Postings"])

    with tab_salary:
        st.subheader("Mean & Median Salary by Discipline (EUR)")
        salary_chart(filtered)
        st.divider()
        salary_table(filtered)

    with tab_ai:
        st.subheader("AI Term Matches by Discipline")
        ai_chart(filtered)
        st.divider()
        st.subheader("Roles with AI Mentions by Discipline")
        ai_pie_charts(filtered)
        st.divider()
        ai_table(filtered)

    with tab_jobs:
        st.subheader("All Postings")
        df = jobs_to_df(filtered)
        if "url" in df.columns:
            st.dataframe(
                df,
                column_config={"url": st.column_config.LinkColumn("URL", display_text="View")},
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.dataframe(df, hide_index=True, use_container_width=True)


# =================================================================================
# ENTRY POINT
# =================================================================================

def init():
    build_page()


if __name__ == "__main__":
    build_page()