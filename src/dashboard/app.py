import os
import duckdb
import streamlit as st
from dotenv import load_dotenv

try:
    # Package-relative import (when imported as src.dashboard.app, e.g. from tests).
    from .queries import latest_status, recent_weather, disruption_vs_weather
except ImportError:
    # `streamlit run src/dashboard/app.py` executes this file as a standalone
    # script with no parent package, so fall back to a sibling-module import.
    from queries import latest_status, recent_weather, disruption_vs_weather

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")

st.set_page_config(page_title="UK Transit + Weather", page_icon="🚇", layout="wide")


@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=60)
def load_latest_status():
    return latest_status(get_connection())


@st.cache_data(ttl=60)
def load_recent_weather(days):
    return recent_weather(get_connection(), days=days)


@st.cache_data(ttl=60)
def load_disruption_vs_weather(days):
    return disruption_vs_weather(get_connection(), days=days)


def status_badge(severity):
    """Bucket TfL's statusSeverity (10 = Good Service) into a rough traffic-light indicator."""
    if severity >= 10:
        return "🟢"
    if severity >= 5:
        return "🟠"
    return "🔴"


st.title("UK Transit + Weather")
st.caption("TfL status + Open-Meteo hourly → DuckDB → Streamlit")

if not os.path.exists(DB_PATH):
    st.warning("No database found yet. Run the ETL once:  `python -m src.etl.run_etl`")
    st.stop()

with st.sidebar:
    st.header("Filters")
    days = st.select_slider("Weather / correlation window (days)", options=[1, 3, 7, 14, 30], value=7)
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

tab_transit, tab_weather, tab_correlation = st.tabs(["🚇 Transit", "🌦️ Weather", "📈 Correlation"])

with tab_transit:
    try:
        status = load_latest_status()
    except duckdb.CatalogException:
        status = None

    if status is None or status.empty:
        st.info("No status rows yet. Run the ETL once:  python -m src.etl.run_etl")
    else:
        line_options = sorted(status["line_id"].unique())
        selected_lines = st.multiselect("Lines", line_options, default=line_options)
        filtered = status[status["line_id"].isin(selected_lines)]

        disrupted = int((filtered["status_severity"] < 10).sum())
        col1, col2 = st.columns(2)
        col1.metric("Good Service", len(filtered) - disrupted)
        col2.metric("Disrupted", disrupted)

        display = filtered.copy()
        display["status"] = display["status_severity"].apply(status_badge) + " " + display["status_description"]
        st.dataframe(
            display[["line_id", "status", "as_of"]],
            width="stretch",
            hide_index=True,
        )

with tab_weather:
    try:
        weather = load_recent_weather(days)
    except duckdb.CatalogException:
        weather = None

    if weather is None or weather.empty:
        st.info("No weather rows yet. Run the ETL once:  python -m src.etl.run_etl")
    else:
        st.subheader(f"Temperature (last {days} days)")
        st.line_chart(weather.set_index("time")["temperature_c"])
        st.subheader(f"Precipitation (last {days} days)")
        st.bar_chart(weather.set_index("time")["precip_mm"])

with tab_correlation:
    try:
        combined = load_disruption_vs_weather(days)
    except duckdb.CatalogException:
        combined = None

    if combined is None or combined.empty:
        st.info("Not enough overlapping status and weather history yet to compare.")
    else:
        st.subheader(f"Disrupted lines vs. rainfall (last {days} days)")
        st.line_chart(combined.set_index("hour")[["disrupted_lines", "precip_mm"]])
        st.caption("Hourly count of disrupted lines plotted against average precipitation (mm).")
