import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("🦠 COVID-19 Data Analysis Dashboard – June 2025")

@st.cache_data
def load_data():
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df = pd.read_csv(url)
    df = df[df["continent"].notna()]  # Remove aggregate regions
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("📌 Filter")
country = st.sidebar.selectbox("Select Country", sorted(df["location"].unique()))
country_data = df[df["location"] == country]

# Display metrics
st.subheader(f"📊 Stats for {country}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cases", f"{int(country_data['total_cases'].max()):,}")
col2.metric("Total Deaths", f"{int(country_data['total_deaths'].max()):,}")
col3.metric("Total Vaccinations", f"{int(country_data['total_vaccinations'].max()):,}")

# Line chart
st.markdown("### 📈 Daily New Cases Over Time")
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(x="date", y="new_cases", data=country_data, ax=ax, color="red")
ax.set_ylabel("New Cases")
st.pyplot(fig)

# Optional: Add more sections (vaccinations over time, death rate, etc.)

