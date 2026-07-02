"""Pure query functions used by the dashboard, kept separate from app.py so they're testable
without running Streamlit."""


def latest_status(conn):
    """Latest status row per line."""
    return conn.execute("""
        select * from (
          select as_of, line_id, status_severity, status_description,
                 row_number() over (partition by line_id order by as_of desc) as rn
          from fact_status
        ) where rn = 1
        order by line_id
    """).df()


def recent_weather(conn, days=7):
    """Hourly weather for the trailing `days` days (excludes forecast hours)."""
    days = int(days)
    return conn.execute(f"""
        select time, temperature_c, precip_mm, windspeed_ms, cloudcover_pct
        from fact_weather_hourly
        where time > CAST(now() AS TIMESTAMP) - interval '{days} day'
          and time <= CAST(now() AS TIMESTAMP)
        order by time
    """).df()


def disruption_vs_weather(conn, days=7):
    """Hourly count of disrupted lines (status_severity < 10) joined with weather,
    to surface whether bad weather correlates with transit disruption."""
    days = int(days)
    return conn.execute(f"""
        with disruption as (
          select date_trunc('hour', as_of) as hour,
                 count(*) filter (where status_severity < 10) as disrupted_lines,
                 count(distinct line_id) as total_lines
          from fact_status
          where as_of > CAST(now() AS TIMESTAMP) - interval '{days} day'
          group by 1
        ),
        weather as (
          select date_trunc('hour', time) as hour,
                 avg(precip_mm) as precip_mm,
                 avg(temperature_c) as temperature_c
          from fact_weather_hourly
          group by 1
        )
        select d.hour, d.disrupted_lines, d.total_lines, w.precip_mm, w.temperature_c
        from disruption d
        join weather w using (hour)
        order by d.hour
    """).df()
