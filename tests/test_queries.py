import duckdb
import pandas as pd

from dashboard.queries import disruption_vs_weather, latest_status, recent_weather

NOW = pd.Timestamp.now(tz="UTC").floor("h")


def _conn_with_status():
    conn = duckdb.connect(":memory:")
    df = pd.DataFrame(
        {
            "as_of": [NOW - pd.Timedelta(hours=1), NOW, NOW],
            "line_id": ["central", "central", "district"],
            "status_severity": [10, 5, 10],
            "status_description": ["Good Service", "Minor Delays", "Good Service"],
        }
    )
    conn.register("df", df)
    conn.execute("CREATE TABLE fact_status AS SELECT * FROM df")
    conn.unregister("df")
    return conn


def test_latest_status_picks_most_recent_row_per_line():
    conn = _conn_with_status()
    result = latest_status(conn)

    assert len(result) == 2
    central = result[result["line_id"] == "central"].iloc[0]
    assert central["status_severity"] == 5


def test_recent_weather_filters_to_window_and_excludes_future():
    conn = duckdb.connect(":memory:")
    df = pd.DataFrame(
        {
            "time": [
                pd.Timestamp.now() - pd.Timedelta(days=10),
                pd.Timestamp.now() - pd.Timedelta(hours=1),
                pd.Timestamp.now() + pd.Timedelta(hours=1),
            ],
            "temperature_c": [1.0, 2.0, 3.0],
            "precip_mm": [0.0, 0.0, 0.0],
            "windspeed_ms": [1.0, 1.0, 1.0],
            "cloudcover_pct": [0, 0, 0],
        }
    )
    conn.register("df", df)
    conn.execute("CREATE TABLE fact_weather_hourly AS SELECT * FROM df")
    conn.unregister("df")

    result = recent_weather(conn, days=7)

    assert len(result) == 1
    assert result.iloc[0]["temperature_c"] == 2.0


def test_disruption_vs_weather_joins_on_hour():
    conn = _conn_with_status()
    weather = pd.DataFrame(
        {
            "time": [NOW - pd.Timedelta(hours=1), NOW],
            "temperature_c": [5.0, 6.0],
            "precip_mm": [0.0, 4.0],
            "windspeed_ms": [1.0, 1.0],
            "cloudcover_pct": [0, 0],
        }
    )
    conn.register("wdf", weather)
    conn.execute("CREATE TABLE fact_weather_hourly AS SELECT * FROM wdf")
    conn.unregister("wdf")

    result = disruption_vs_weather(conn, days=1)

    assert len(result) == 2
    disrupted_hour = result[result["disrupted_lines"] == 1].iloc[0]
    assert disrupted_hour["precip_mm"] == 4.0
