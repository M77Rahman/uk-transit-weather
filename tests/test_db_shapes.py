import duckdb, os
DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")
def test_tables_exist():
    con = duckdb.connect(DB_PATH)
    tables = {r[0] for r in con.execute("show tables").fetchall()}
    assert {"fact_status","fact_weather_hourly"} <= tables
