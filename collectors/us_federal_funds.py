"""US Federal Funds Rate — Federal Reserve H.15 release.

Source: https://www.federalreserve.gov/releases/h15/
Returns the effective federal funds rate for the most recent complete months.

The FEDFUNDS series (FRED) is a monthly average. This collector reads the current
effective rate from the H.15 page and assigns it to the current month. It is
accurate for months where the rate did not change; for months spanning an FOMC
decision, the value may differ slightly from the true monthly average.
"""

import calendar
import re
import urllib.request
from datetime import date


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://www.federalreserve.gov/releases/h15/"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Find the effective federal funds rate
    m = re.search(r"effective federal funds rate[^<]*?(\d+\.\d+)%", html, re.IGNORECASE)
    if not m:
        # Try alternate pattern from H.15 data table
        m = re.search(r"Federal funds.*?(\d+\.\d+)", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return []

    rate = m.group(1)
    today = date.today()
    # Return the current month — update.py will skip if date already exists in CSV
    return [(_month_end(today.year, today.month), rate)]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.federalreserve.gov/releases/h15/ manually")
