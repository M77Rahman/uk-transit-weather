import os, duckdb, pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")
conn = duckdb.connect(DB_PATH, read_only=True)

st.set_page_config(page_title="UK Transit + Weather", layout="wide")
st.title("UK Transit + Weather")
st.caption("TfL status + Open-Meteo hourly → DuckDB → Streamlit")

# --- Line status (latest per line)
st.subheader("Current line status (latest per line)")
status = conn.execute("""
select * from (
  select as_of, line_id, status_severity, status_description,
         row_number() over (partition by line_id order by as_of desc) as rn
  from fact_status
) where rn = 1
order by line_id
""").df()
st.dataframe(status, width='stretch')  # deprecation-safe

# --- Weather last 7 days (timezone-safe comparison)
st.subheader("Temperature (last 7 days)")
weather = conn.execute("""
select time, temperature_c
from fact_weather_hourly
where time > CAST(now() AS TIMESTAMP) - interval 7 day
order by time
""").df()

if not weather.empty:
    weather = weather.set_index("time")
    st.line_chart(weather["temperature_c"])
else:
    st.info("No weather rows yet. Run the ETL once:  python -m src.etl.run_etl")
