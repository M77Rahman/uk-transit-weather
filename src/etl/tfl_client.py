import os, requests

BASE = "https://api.tfl.gov.uk"
APP_KEY = os.getenv("TFL_APP_KEY")

def _auth():
    return {"app_key": APP_KEY} if APP_KEY else {}

def get_line_status():
    """Snapshot of status for tube/overground/dlr/elizabeth-line."""
    url = f"{BASE}/Line/Mode/tube,overground,dlr,elizabeth-line/Status"
    r = requests.get(url, params=_auth(), timeout=20)
    r.raise_for_status()
    return r.json()
