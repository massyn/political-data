"""US GDP Growth (quarterly, QoQ%) — Trading Economics HTML scrape.

Source: https://tradingeconomics.com/united-states/gdp-growth
Returns quarter-on-quarter percentage change (not annualised).

FRAGILE: If Trading Economics blocks requests, get the latest value from
https://www.bea.gov/data/gdp/gross-domestic-product and add it manually.
BEA API (free key at apps.bea.gov) can also provide this programmatically.

The BEA publishes three estimates per quarter:
  • Advance (month 1 after quarter end)
  • Second estimate (month 2)
  • Third/final (month 3)
Use the most recently published estimate.
"""

import calendar
import re
import urllib.request


_QUARTERS = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}


def _quarter_end(year: int, quarter_month: int) -> str:
    return f"{year}-{quarter_month:02d}-{calendar.monthrange(year, quarter_month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://tradingeconomics.com/united-states/gdp-growth"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Pattern: "Q4 2025: 0.5% quarter-on-quarter" or "Q1 2026 at 0.5%"
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
        print("No data — check https://www.bea.gov/data/gdp/gross-domestic-product manually")
