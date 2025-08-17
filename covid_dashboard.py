import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="COVID-19 Dashboard",
    layout="wide"
)

st.title("COVID-19 Global Dashboard – WHO Data")

# Load data
@st.cache_data
def load_who_data():
    df = pd.read_csv("WHO-COVID-19-global-daily-data.csv", parse_dates=["Date_reported"])
    df.rename(columns={
        "Date_reported": "Date",
        "Country": "Country",
        "New_cases": "New Cases",
        "Cumulative_cases": "Total Cases",
        "New_deaths": "New Deaths",
        "Cumulative_deaths": "Total Deaths"
    }, inplace=True)
    return df

@st.cache_data
def load_vacc_data():
    df = pd.read_csv("daily-covid-19-vaccine-doses-administered-per-million-people.csv")
    df.rename(columns={
        "Entity": "Country",
        "Day": "Date",
        "COVID-19 doses (daily, 7-day average, per million people)": "Doses per Million"
    }, inplace=True)
    df["Day"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


cases_df = load_who_data()
vacc_df = load_vacc_data()

# Sidebar filters
st.sidebar.header("Filters")
country_list = sorted(cases_df["Country"].unique())
country = st.sidebar.selectbox("Select Country", country_list)

# Date range filter
country_cases = cases_df[cases_df["Country"] == country]
min_date = country_cases["Date"].min().date()
max_date = country_cases["Date"].max().date()

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

filtered_cases = country_cases[
    (country_cases["Date"] >= pd.to_datetime(date_range[0])) &
    (country_cases["Date"] <= pd.to_datetime(date_range[1]))
]

country_vacc = vacc_df[vacc_df["Country"] == country]

# KPIs - Cases/Deaths
total_cases = filtered_cases["Total Cases"].max()
total_deaths = filtered_cases["Total Deaths"].max()
total_new_cases = filtered_cases["New Cases"].sum()
total_new_deaths = filtered_cases["New Deaths"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cases", f"{total_cases:,}")
col2.metric("Total Deaths", f"{total_deaths:,}")
col3.metric("New Cases (Selected Range)", f"{total_new_cases:,}")
col4.metric("New Deaths (Selected Range)", f"{total_new_deaths:,}")

# Charts - Cases/Deaths
st.subheader("Daily New Cases Over Time")
fig_cases = px.line(filtered_cases, x="Date", y="New Cases", title=f"Daily New Cases in {country}", markers=True)
st.plotly_chart(fig_cases, use_container_width=True)

st.subheader("Daily New Deaths Over Time")
fig_deaths = px.line(filtered_cases, x="Date", y="New Deaths", title=f"Daily New Deaths in {country}", markers=True)
st.plotly_chart(fig_deaths, use_container_width=True)

# Chart - Vaccinations
if not country_vacc.empty:
    st.subheader("Vaccination Progress Over Time (per million people)")
    fig_vacc = px.line(country_vacc, x="Date", y="Doses per Million",
                       title=f"COVID-19 Vaccine Doses in {country} (7-day avg per million)")
    st.plotly_chart(fig_vacc, use_container_width=True)

# Global Top 10
st.subheader("Top 10 Countries by Total Cases (Latest Data)")
latest_data = cases_df.sort_values("Date").groupby("Country").tail(1)
top10_cases = latest_data.sort_values("Total Cases", ascending=False).head(10)

fig_top10 = px.bar(
    top10_cases,
    x="Total Cases",
    y="Country",
    orientation="h",
    title="Top 10 Countries by Total Cases",
    color="Total Cases",
    color_continuous_scale="Reds"
)
fig_top10.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_top10, use_container_width=True)

# Footer
st.caption("Data Source: World Health Organization (WHO) & Our World in Data") 
