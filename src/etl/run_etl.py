import logging

from dotenv import load_dotenv

from .load import append_df, get_conn, upsert_df
from .tfl_client import get_line_status
from .transform import normalize_line_status, normalize_weather_hourly
from .weather_client import get_hourly_weather

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("etl")


def run_status(conn):
    """Fetch and load the TfL line status snapshot. Returns rows loaded, or None on failure."""
    try:
        lines_json = get_line_status()
        ls = normalize_line_status(lines_json)
        n = append_df(conn, ls, "fact_status")
        log.info("line_status rows inserted: %d", n)
        return n
    except Exception:
        log.exception("TfL line status fetch/load failed; continuing with other sources")
        return None


def run_weather(conn):
    """Fetch and load hourly weather. Returns rows loaded, or None on failure."""
    try:
        weather_json = get_hourly_weather()
        wh = normalize_weather_hourly(weather_json)
        n = upsert_df(conn, wh, "fact_weather_hourly", key_cols=["time"])
        log.info("weather_hourly rows upserted: %d", n)
        return n
    except Exception:
        log.exception("Weather fetch/load failed; continuing with other sources")
        return None


def main():
    load_dotenv()
    conn = get_conn()

    status_rows = run_status(conn)
    weather_rows = run_weather(conn)

    if status_rows is None and weather_rows is None:
        raise SystemExit("[ETL] both sources failed; see log above")


if __name__ == "__main__":
    main()
