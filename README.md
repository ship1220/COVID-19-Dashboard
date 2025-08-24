# COVID-19-Dashboard

## Project Overview
This project analyzes the daily COVID-19 vaccine doses administered per million people across different countries.  
The dataset provides insights into how vaccination efforts progressed globally, with a focus on trends and comparisons across time and regions.

To view the project- [Open the Streamlit Dashboard](https://covid-19-dashboard-2kv65k9mlqeyvccmphthwg.streamlit.app/)

## Dataset
- **File Used**: - `WHO-COVID-19-global-daily-data.csv` (Daily new cases and deaths)
- `daily-covid-19-vaccine-doses-administered-per-million-people.csv` (Vaccination trends)

  
## Objectives
1. Preprocess and clean the dataset (rename columns, convert dates to datetime format).
2. Perform exploratory data analysis (EDA) to understand daily new cases, deaths and vaccination progress across countries.
3. Generate KPIs and visualizations to analyse the spread and vaccination process.

## Key Insights & KPIs
- **Vaccination Rollouts & Access**: Countries with consistent and timely vaccination rollouts saw steady coverage growth, while uneven distribution highlighted global inequality in access.

- **Waves of Daily New Cases** : The pandemic unfolded in multiple waves, with infection peaks often arriving before vaccination campaigns scaled up, showing delayed responses in several regions.

- **Lag Between Cases & Deaths**: Death rates typically spiked 2–3 weeks after new case surges, establishing deaths as a lagging indicator of infections.

- **Impact of Vaccination on Outcomes**: Faster and broader vaccination coverage correlated with shorter waves, reduced severity of infections, and declining death-to-case ratios, proving vaccine effectiveness.

- **Vaccination vs. Cases & Deaths**: A clear negative correlation emerged: higher vaccination rates flattened case curves and lowered death rates. Even when cases surged due to variants, booster drives prevented proportional rises in mortality.

## Technologies Used
- **Python**
- **Pandas** → Data cleaning and manipulation
- **Plotly Express** →Interactive Data visualization
- **Jupyter Notebook** → Development environment
- **Streamlit** → Deployment environment
