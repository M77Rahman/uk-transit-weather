import duckdb, os, pytest
DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")

@pytest.mark.skipif(not os.path.exists(DB_PATH), reason="DB not generated yet")
def test_tables_exist():
    con = duckdb.connect(DB_PATH, read_only=True)
    tables = {r[0] for r in con.execute("show tables").fetchall()}
    assert {"fact_status","fact_weather_hourly"} <= tables
