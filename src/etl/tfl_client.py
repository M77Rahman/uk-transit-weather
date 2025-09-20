import os, time, requests

BASE = "https://api.tfl.gov.uk"
APP_KEY = os.getenv("TFL_APP_KEY")

def _auth():
    return {"app_key": APP_KEY} if APP_KEY else {}

def _get(url, params=None, tries=3, timeout=20):
    params = params or {}
    backoff = 1.0
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent":"uk-transit-weather/1.0"})
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if i == tries - 1:
                raise
            time.sleep(backoff)
            backoff *= 2
    return []

def get_line_status():
    """Snapshot status for tube/overground/dlr/elizabeth-line."""
    url = f"{BASE}/Line/Mode/tube,overground,dlr,elizabeth-line/Status"
    return _get(url, params=_auth())
