import duckdb
import pandas as pd

from etl.load import append_df, upsert_df


def test_append_df_accumulates_rows():
    conn = duckdb.connect(":memory:")
    df1 = pd.DataFrame({"line_id": ["central"], "status_severity": [10]})
    df2 = pd.DataFrame({"line_id": ["central"], "status_severity": [5]})

    append_df(conn, df1, "fact_status")
    append_df(conn, df2, "fact_status")

    assert conn.execute("select count(*) from fact_status").fetchone()[0] == 2


def test_upsert_df_replaces_rows_with_matching_key():
    conn = duckdb.connect(":memory:")
    first = pd.DataFrame(
        {
            "time": pd.to_datetime(["2025-01-01T00:00", "2025-01-01T01:00"]),
            "temperature_c": [1.0, 2.0],
        }
    )
    upsert_df(conn, first, "fact_weather_hourly", key_cols=["time"])

    # Second run overlaps one hour (forecast re-fetched) and adds a new one.
    second = pd.DataFrame(
        {
            "time": pd.to_datetime(["2025-01-01T01:00", "2025-01-01T02:00"]),
            "temperature_c": [99.0, 3.0],
        }
    )
    upsert_df(conn, second, "fact_weather_hourly", key_cols=["time"])

    result = conn.execute("select time, temperature_c from fact_weather_hourly order by time").df()
    assert len(result) == 3
    assert (
        result.loc[result["time"] == pd.Timestamp("2025-01-01T01:00"), "temperature_c"].iloc[0]
        == 99.0
    )


def test_upsert_df_empty_is_noop():
    conn = duckdb.connect(":memory:")
    empty = pd.DataFrame({"time": pd.to_datetime([]), "temperature_c": pd.Series(dtype=float)})
    assert upsert_df(conn, empty, "fact_weather_hourly", key_cols=["time"]) == 0
