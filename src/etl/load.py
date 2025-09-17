import duckdb, os

DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH)

def append_df(conn, df, table):
    if df is None or df.empty:
        return
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0")
    conn.register("df", df)
    conn.execute(f"INSERT INTO {table} SELECT * FROM df")
    conn.unregister("df")
