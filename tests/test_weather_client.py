from etl import weather_client


class _FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"hourly": {"time": []}}


def test_get_hourly_weather_requests_past_and_forecast_days(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None, headers=None):
        captured["params"] = params
        return _FakeResponse()

    monkeypatch.setattr(weather_client.requests, "get", fake_get)

    weather_client.get_hourly_weather()

    assert captured["params"]["past_days"] == 7
    assert captured["params"]["forecast_days"] == 7
