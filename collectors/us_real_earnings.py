"""US Real Average Hourly Earnings (quarterly, 1982-84$) — FRED API series LES1252881600Q.

Requires environment variable: FRED_API_KEY
Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html

Without a FRED key this collector cannot run. The series is not available via the
BLS public API. Manually look up the value at:
  https://fred.stlouisfed.org/series/LES1252881600Q
and append a row to data.csv in the format: YYYY-MM-DD,value
"""

import calendar
import json
import os
import urllib.request


def _quarter_end(year: int, quarter: int) -> str:
    month = quarter * 3
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FRED_API_KEY not set. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html "
            "or update manually from https://fred.stlouisfed.org/series/LES1252881600Q"
        )
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id=LES1252881600Q&api_key={api_key}&file_type=json"
        f"&sort_order=desc&limit=8"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "political-data-collector/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    rows = []
    for obs in data.get("observations", []):
        if obs["value"] == ".":
            continue
        d = obs["date"]  # already YYYY-MM-DD (first of quarter); convert to end-of-quarter
        year, month = int(d[:4]), int(d[5:7])
        quarter = (month - 1) // 3 + 1
        rows.append((_quarter_end(year, quarter), obs["value"]))
    rows.sort()
    return rows[-6:]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — set FRED_API_KEY or update manually from https://fred.stlouisfed.org/series/LES1252881600Q")
