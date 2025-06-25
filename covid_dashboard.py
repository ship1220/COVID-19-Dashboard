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
# Date range filter
min_date = country_data["date"].min().date()
max_date = country_data["date"].max().date()

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter country_data based on date range
filtered_data = country_data[
    (country_data["date"] >= pd.to_datetime(date_range[0])) &
    (country_data["date"] <= pd.to_datetime(date_range[1]))
]



# Display metrics
st.subheader(f"📊 Stats for {country}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cases", f"{int(country_data['total_cases'].max()):,}")
col2.metric("Total Deaths", f"{int(country_data['total_deaths'].max()):,}")
col3.metric("Total Vaccinations", f"{int(country_data['total_vaccinations'].max()):,}")

# Line chart
st.markdown("### 📈 Daily New Cases Over Time")
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(x="date", y="new_cases", data=filtered_data, ax=ax, color="red")

ax.set_ylabel("New Cases")
st.pyplot(fig)
st.markdown("## 🌍 Top 10 Countries by Total Cases")

# Safely get latest data for each country
latest_data = df.sort_values("date").groupby("location").tail(1)
latest_data = latest_data[latest_data["continent"].notna()]  # Remove aggregate entries
latest_data = latest_data.dropna(subset=["total_cases"])

# Get Top 10 by total cases
top_10 = latest_data.sort_values("total_cases", ascending=False).head(10)
plt.style.use("dark_background")

# Plot bar chart
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x="total_cases", y="location", data=top_10, palette="Reds_r", ax=ax2)
ax2.set_xlabel("Total Cases")
ax2.set_ylabel("Country")
ax2.set_title("Top 10 Countries by Total COVID-19 Cases")
plt.tight_layout()

st.pyplot(fig2)



# Optional: Add more sections (vaccinations over time, death rate, etc.)

