import os, duckdb
import streamlit as st
from dotenv import load_dotenv

from .queries import latest_status, recent_weather, disruption_vs_weather

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")
conn = duckdb.connect(DB_PATH, read_only=True)

st.set_page_config(page_title="UK Transit + Weather", layout="wide")
st.title("UK Transit + Weather")
st.caption("TfL status + Open-Meteo hourly → DuckDB → Streamlit")

# --- Line status (latest per line)
st.subheader("Current line status (latest per line)")
status = latest_status(conn)

if not status.empty:
    disrupted = int((status["status_severity"] < 10).sum())
    col1, col2 = st.columns(2)
    col1.metric("Lines with Good Service", len(status) - disrupted)
    col2.metric("Lines disrupted", disrupted)
    st.dataframe(status, width='stretch')
else:
    st.info("No status rows yet. Run the ETL once:  python -m src.etl.run_etl")

# --- Weather last 7 days
st.subheader("Temperature (last 7 days)")
weather = recent_weather(conn, days=7)

if not weather.empty:
    st.line_chart(weather.set_index("time")["temperature_c"])
else:
    st.info("No weather rows yet. Run the ETL once:  python -m src.etl.run_etl")

# --- Disruption vs weather correlation
st.subheader("Disrupted lines vs. rainfall (last 7 days)")
combined = disruption_vs_weather(conn, days=7)

if not combined.empty:
    st.line_chart(combined.set_index("hour")[["disrupted_lines", "precip_mm"]])
    st.caption("Hourly count of disrupted lines plotted against average precipitation (mm).")
else:
    st.info("Not enough overlapping status and weather history yet to compare.")
