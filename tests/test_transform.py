from etl.transform import normalize_weather_hourly

def test_weather_cols():
    sample = {"hourly":{
        "time":["2025-01-01T00:00"],
        "temperature_2m":[1.0],
        "precipitation":[0.0],
        "windspeed_10m":[2.0],
        "cloudcover":[10]
    }}
    df = normalize_weather_hourly(sample)
    assert {"time","temperature_c","precip_mm","windspeed_ms","cloudcover_pct"} <= set(df.columns)
