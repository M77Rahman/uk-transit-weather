import pandas as pd

def normalize_line_status(lines_json):
    rows=[]
    as_of = pd.Timestamp.now(tz="UTC")  # fixed
    for line in lines_json:
        for st in line.get("lineStatuses", []):
            rows.append({
                "as_of": as_of,
                "line_id": line["id"],
                "status_severity": st.get("statusSeverity"),
                "status_description": st.get("statusSeverityDescription"),
            })
    return pd.DataFrame(rows)

def normalize_weather_hourly(weather_json):
    h = weather_json["hourly"]
    return pd.DataFrame({
        "time": pd.to_datetime(h["time"]),
        "temperature_c": h["temperature_2m"],
        "precip_mm": h["precipitation"],
        "windspeed_ms": h["windspeed_10m"],
        "cloudcover_pct": h["cloudcover"],
    })
