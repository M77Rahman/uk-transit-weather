from dotenv import load_dotenv
from .tfl_client import get_line_status
from .weather_client import get_hourly_weather
from .transform import normalize_line_status, normalize_weather_hourly
from .load import get_conn, append_df

def main():
    load_dotenv()
    conn = get_conn()

    # TfL status snapshot
    lines_json = get_line_status()
    ls = normalize_line_status(lines_json)
    append_df(conn, ls, "fact_status")
    print(f"[ETL] line_status rows inserted: {len(ls)}")

    # Weather hourly
    weather_json = get_hourly_weather()
    wh = normalize_weather_hourly(weather_json)
    append_df(conn, wh, "fact_weather_hourly")
    print(f"[ETL] weather_hourly rows inserted: {len(wh)}")

if __name__ == "__main__":
    main()
