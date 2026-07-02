import duckdb, os

DB_PATH = os.getenv("DB_PATH", "data/uk_transit_weather.duckdb")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH)

def append_df(conn, df, table):
    """Append rows as-is. Use for append-only event logs (e.g. status snapshots)."""
    if df is None or df.empty:
        return 0
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0")
    conn.register("df", df)
    conn.execute(f"INSERT INTO {table} SELECT * FROM df")
    conn.unregister("df")
    return len(df)

def upsert_df(conn, df, table, key_cols):
    """Insert rows, replacing any existing rows with matching key_cols.

    Without this, re-running the ETL against a forecast API that returns
    overlapping time ranges (e.g. hourly weather) would duplicate every
    overlapping row on each run.
    """
    if df is None or df.empty:
        return 0
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0")
    conn.register("df", df)
    keys = ", ".join(key_cols)
    conn.execute(f"DELETE FROM {table} WHERE ({keys}) IN (SELECT {keys} FROM df)")
    conn.execute(f"INSERT INTO {table} SELECT * FROM df")
    conn.unregister("df")
    return len(df)
