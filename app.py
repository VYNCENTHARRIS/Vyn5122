# app.py
# Code snippet assisted by ChatGPT (OpenAI)

import streamlit as st
import pandas as pd
import altair as alt

# ---------- Page config ----------
st.set_page_config(
    page_title="Handwashing & Maternal Mortality – Semmelweis",
    page_icon="🧼",
    layout="wide"
)

# ---------- Data loading ----------
@st.cache_data
def load_data():
    # Make sure this filename matches what you downloaded from Canvas
    df = pd.read_csv("yearly_deaths_by_clinic-1.csv")
    # Standardize column names just in case
    df.columns = [c.strip().title() for c in df.columns]
    df["MortalityRate"] = df["Deaths"] / df["Birth"] * 100
    return df

df = load_data()
handwashing_year = 1847  # Semmelweis introduces handwashing in Clinic 1

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

clinics = st.sidebar.multiselect(
    "Select clinic(s)",
    options=sorted(df["Clinic"].unique()),
    default=sorted(df["Clinic"].unique())
)

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Select year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)

filtered = df[
    df["Clinic"].isin(clinics)
    & df["Year"].between(year_range[0], year_range[1])
]

# ---------- Title & description ----------
st.title("🧼 Dr. Ignaz Semmelweis and the Power of Handwashing")

st.markdown(
    """
In the mid-1800s at the Vienna General Hospital, Dr. Ignaz Semmelweis noticed that
one maternity clinic had a much higher mortality rate from childbed fever than the other.
He introduced **handwashing with chlorinated lime** for doctors and midwives, and deaths dropped sharply.
"""
)

# ---------- Key metrics (before vs after handwashing) ----------
col1, col2 = st.columns(2)

before = df[df["Year"] < handwashing_year]
after = df[df["Year"] >= handwashing_year]

if clinics:
    before = before[before["Clinic"].isin(clinics)]
    after = after[after["Clinic"].isin(clinics)]

avg_before = before["MortalityRate"].mean()
avg_after = after["MortalityRate"].mean()

with col1:
    st.subheader("Average mortality *before* handwashing")
    st.metric(
        label="Mean mortality rate",
        value=f"{avg_before:.2f} %" if pd.notna(avg_before) else "N/A"
    )

with col2:
    st.subheader("Average mortality *after* handwashing")
    st.metric(
        label="Mean mortality rate",
        value=f"{avg_after:.2f} %" if pd.notna(avg_after) else "N/A",
        delta=f"{avg_after - avg_before:+.2f} pp" if pd.notna(avg_before) else None
    )

# ---------- Visualization: mortality over time ----------
st.subheader("Mortality rate over time by clinic")

if filtered.empty:
    st.warning("No data available for the current filter selection.")
else:
    # Code snippet assisted by ChatGPT (OpenAI): Altair chart configuration
    base = alt.Chart(filtered).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("MortalityRate:Q", title="Mortality rate (%)"),
        color=alt.Color("Clinic:N", title="Clinic")
    )

    line = base.mark_line(point=True).interactive()

    # Vertical rule showing handwashing introduction
    rule = alt.Chart(
        pd.DataFrame({"Year": [handwashing_year]})
    ).mark_rule(strokeDash=[4, 4]).encode(
        x="Year:O"
    )

    text = alt.Chart(
        pd.DataFrame({"Year": [handwashing_year], "MortalityRate": [filtered["MortalityRate"].max()]})
    ).mark_text(
        align="left",
        dx=5,
        dy=-5
    ).encode(
        x="Year:O",
        y=alt.value(0),
        text=alt.value("Handwashing introduced")
    )

    chart = (line + rule + text).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

# ---------- Visualization: births vs deaths ----------
st.subheader("Births vs. deaths by year and clinic")

if not filtered.empty:
    # Code snippet assisted by ChatGPT (OpenAI): Bar chart configuration
    births_deaths = filtered.melt(
        id_vars=["Year", "Clinic"],
        value_vars=["Birth", "Deaths"],
        var_name="Type",
        value_name="Count"
    )

    chart_bd = alt.Chart(births_deaths).mark_bar().encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Count:Q", title="Number of births/deaths"),
        color=alt.Color("Type:N", title=""),
        column=alt.Column("Clinic:N", title="Clinic")
    ).properties(
        height=300
    )

    st.altair_chart(chart_bd, use_container_width=True)

# ---------- Findings text inside the app ----------
st.subheader("What do we learn from this data?")

st.write(
    """
Across the selected clinics, mortality rates are **much higher before 1847** and drop
substantially after the introduction of handwashing. Even though the number of births
stays relatively high, the percentage of women dying from childbed fever falls, providing
strong evidence that **simple hygiene practices saved many lives**.
"""
)

st.caption("Note: Some code and text layout were assisted by ChatGPT (OpenAI).")
