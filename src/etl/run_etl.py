from dotenv import load_dotenv
from .tfl_client import get_line_status
from .weather_client import get_hourly_weather
from .transform import normalize_line_status, normalize_weather_hourly
from .load import get_conn, append_df

def main():
    load_dotenv()
    conn = get_conn()

    # TfL status snapshot
    ls = normalize_line_status(get_line_status())
    append_df(conn, ls, "fact_status")

    # Weather hourly
    wh = normalize_weather_hourly(get_hourly_weather())
    append_df(conn, wh, "fact_weather_hourly")

if __name__ == "__main__":
    main()
