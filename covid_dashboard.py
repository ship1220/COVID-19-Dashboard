import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="WHO-style COVID Dashboard")

# -------------------------
# Load data (local fallback -> remote)
# -------------------------
@st.cache_data(ttl=60 * 60 * 6)  # cache for 6 hours
def load_who_data():
    local_path = "/WHO-COVID-19-global-daily-data.csv"
    remote_url = "https://data.who.int/dashboards/covid19/data?n=c"

    if os.path.exists(local_path):
        try:
            df = pd.read_csv(local_path, parse_dates=["Date_reported"])
            source = f"local: {local_path}"
        except Exception as e:
            st.warning(f"Failed to read local file ({e}). Trying remote WHO CSV...")
            df = pd.read_csv(remote_url, parse_dates=["Date_reported"])
            source = f"remote: {remote_url}"
    else:
        # fallback to remote
        df = pd.read_csv(remote_url, parse_dates=["Date_reported"])
        source = f"remote: {remote_url}"

    # normalize column names to simpler ones
    df = df.rename(columns={
        "Date_reported": "date",
        "Country": "country",
        "WHO_region": "who_region",
        "New_cases": "new_cases",
        "Cumulative_cases": "total_cases",
        "New_deaths": "new_deaths",
        "Cumulative_deaths": "total_deaths"
    })

    # ensure numeric types and fillna
    for col in ["new_cases", "total_cases", "new_deaths", "total_deaths"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df, source

df, data_source = load_who_data()

# -------------------------
# Sidebar: filters
# -------------------------
st.sidebar.title("Filters")
st.sidebar.markdown(f"**Data source:** {data_source}")

all_countries = sorted(df["country"].unique())
country_selection = st.sidebar.selectbox("Country", ["World"] + all_countries, index=0)

# Date range defaults to last 365 days or full range if shorter
min_date = df["date"].min().date()
max_date = df["date"].max().date()
default_start = max_date - timedelta(days=365) if (max_date - min_date).days > 365 else min_date

date_range = st.sidebar.date_input("Date range", value=(default_start, max_date), min_value=min_date, max_value=max_date)

# smoothing option
smoothing = st.sidebar.slider("Smoothing window (days) for series", min_value=1, max_value=21, value=7)

# -------------------------
# Data prep based on filters
# -------------------------
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

if country_selection == "World":
    # aggregate worldwide by date
    timeseries = (
        df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        .groupby("date")[["new_cases", "new_deaths", "total_cases", "total_deaths"]]
        .sum()
        .reset_index()
    )
    # for map and top table use most recent per country
    latest_by_country = df.sort_values("date").groupby("country").tail(1)
else:
    timeseries = df[(df["country"] == country_selection) & (df["date"] >= start_date) & (df["date"] <= end_date)].sort_values("date")
    latest_by_country = df.sort_values("date").groupby("country").tail(1)

# rolling smoothing for visualization
if smoothing > 1:
    timeseries["new_cases_smooth"] = timeseries["new_cases"].rolling(smoothing, min_periods=1, center=True).mean()
    timeseries["new_deaths_smooth"] = timeseries["new_deaths"].rolling(smoothing, min_periods=1, center=True).mean()
else:
    timeseries["new_cases_smooth"] = timeseries["new_cases"]
    timeseries["new_deaths_smooth"] = timeseries["new_deaths"]

# -------------------------
# Top KPIs row
# -------------------------
st.title("Number of COVID-19 cases reported to WHO")
st.markdown(f"Data source: **WHO** (loaded from `{data_source}`) — Showing **{country_selection}**")

# compute KPI values (use last available row of timeseries)
if not timeseries.empty:
    last = timeseries.iloc[-1]
    k_total_cases = int(last["total_cases"]) if "total_cases" in last else int(df["total_cases"].max())
    k_total_deaths = int(last["total_deaths"]) if "total_deaths" in last else int(df["total_deaths"].max())
    k_new_cases = int(last["new_cases"]) if "new_cases" in last else 0
    k_new_deaths = int(last["new_deaths"]) if "new_deaths" in last else 0
else:
    k_total_cases = int(df["total_cases"].max())
    k_total_deaths = int(df["total_deaths"].max())
    k_new_cases = 0
    k_new_deaths = 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total cases", f"{k_total_cases:,}")
c2.metric("Total deaths", f"{k_total_deaths:,}")
c3.metric("New cases (latest)", f"{k_new_cases:,}")
c4.metric("New deaths (latest)", f"{k_new_deaths:,}")

st.markdown("---")

# -------------------------
# Time series charts (Weekly and Daily)
# -------------------------
left, right = st.columns([2, 1])

with left:
    st.subheader("Recent COVID-19 cases reported to WHO (daily)")
    fig_cases = go.Figure()
    fig_cases.add_trace(go.Scatter(
        x=timeseries["date"],
        y=timeseries["new_cases_smooth"],
        mode="lines",
        name=f"New cases (smoothed, {smoothing}d)",
        line=dict(color="#0072B2"),
        fill='tozeroy',
        fillcolor='rgba(0,114,178,0.15)'
    ))
    fig_cases.update_layout(margin=dict(t=30, b=10, l=0, r=0), yaxis_title="New cases", xaxis_title=None)
    st.plotly_chart(fig_cases, use_container_width=True, theme="streamlit")

with right:
    st.subheader("Recent COVID-19 deaths reported to WHO (daily)")
    fig_deaths = go.Figure()
    fig_deaths.add_trace(go.Bar(x=timeseries["date"], y=timeseries["new_deaths_smooth"], name="New deaths", marker_color="#D55E00"))
    fig_deaths.update_layout(margin=dict(t=30, b=10, l=0, r=0), yaxis_title="New deaths", xaxis_title=None)
    st.plotly_chart(fig_deaths, use_container_width=True, theme="streamlit")

st.markdown("---")

# -------------------------
# Top countries table and map
# -------------------------
st.subheader("Number of COVID-19 cases reported to WHO (by country)")

# prepare a top table of latest_by_country
table_df = latest_by_country[["country", "total_cases", "total_deaths", "new_cases", "new_deaths", "who_region"]].copy()
table_df = table_df.sort_values("total_cases", ascending=False).reset_index(drop=True)

# show top N with option
top_n = st.selectbox("Show top how many countries?", [10, 20, 50, 100], index=0)
st.dataframe(table_df.head(top_n).style.format({"total_cases": "{:,}", "total_deaths": "{:,}", "new_cases": "{:,}", "new_deaths":"{: ,}"}))

# choropleth map
st.markdown("### Map: Cumulative cases by country (latest)")
map_df = table_df.copy()
# Plotly choropleth expects either ISO codes or country names; we'll use country names
fig_map = px.choropleth(
    map_df,
    locations="country",
    locationmode="country names",
    color="total_cases",
    hover_name="country",
    hover_data={"total_cases": True, "total_deaths": True, "new_cases": True},
    color_continuous_scale="Reds",
    title="Cumulative confirmed cases (latest)",
)
fig_map.update_layout(margin=dict(t=40, b=0, l=0, r=0), coloraxis_colorbar={'title':'Cases'})
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# -------------------------
# Additional: weekly aggregation plot (to mimic WHO weekly)
# -------------------------
st.subheader("Recent COVID-19 cases reported to WHO (weekly)")

# weekly aggregation across world or country
if country_selection == "World":
    weekly = df.groupby(pd.Grouper(key="date", freq="W-MON"))[["new_cases", "new_deaths"]].sum().reset_index()
else:
    sub = df[df["country"] == country_selection]
    weekly = sub.groupby(pd.Grouper(key="date", freq="W-MON"))[["new_cases", "new_deaths"]].sum().reset_index()

fig_week = go.Figure()
fig_week.add_trace(go.Scatter(x=weekly["date"], y=weekly["new_cases"], mode="lines", fill="tozeroy", name="Weekly cases", line=dict(color="#4DB6AC")))
fig_week.update_layout(margin=dict(t=30, b=10, l=0, r=0), yaxis_title="Weekly cases")
st.plotly_chart(fig_week, use_container_width=True)

# -------------------------
# Footer / Notes
# -------------------------
st.markdown("---")
st.markdown("**Notes:** Data are reported daily to WHO by member states. This dashboard uses the WHO CSV snapshot and is intended to visually resemble WHO's official dashboard for exploration and learning.")
