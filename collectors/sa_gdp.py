"""SA GDP Growth (quarterly QoQ%) — Trading Economics HTML scrape.

Source: https://tradingeconomics.com/south-africa/gdp-growth

StatsSA publishes quarterly GDP approximately 3 months after the quarter ends.

FRAGILE: Trading Economics may block automated requests. If this fails, visit:
  https://www.statssa.gov.za/ → Publications → P0441 Gross Domestic Product
and add the quarterly growth rate to data.csv manually.
"""

import calendar
import re
import urllib.request


_QUARTERS = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}


def _quarter_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://tradingeconomics.com/south-africa/gdp-growth"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Pattern: "Q4 2025: 0.4% quarter-on-quarter"
    pattern = r"(Q[1-4])\s+(\d{4})[^\d]{0,30}?(-?\d+\.?\d*)\s*%"
    rows = []
    for q, year, val in re.findall(pattern, html, re.IGNORECASE):
        month = _QUARTERS.get(q.upper())
        if month:
            rows.append((_quarter_end(int(year), month), val))
    rows = sorted(set(rows))
    return rows[-4:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.statssa.gov.za/ → P0441 Gross Domestic Product manually")
