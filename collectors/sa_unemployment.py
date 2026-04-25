"""SA Unemployment Rate (quarterly, %) — Trading Economics HTML scrape.

Source: https://tradingeconomics.com/south-africa/unemployment-rate

StatsSA publishes the Quarterly Labour Force Survey (QLFS) approximately
6-8 weeks after each quarter ends (Feb, May, Aug, Nov for Q4/Q1/Q2/Q3).

FRAGILE: Trading Economics may block automated requests. If this fails, visit:
  https://www.statssa.gov.za/ → Publications → P0211 Quarterly Labour Force Survey
and add the quarterly rate to data.csv manually.
"""

import calendar
import re
import urllib.request


_QUARTERS = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}


def _quarter_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://tradingeconomics.com/south-africa/unemployment-rate"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Pattern: "Q4 2025: 31.4%" or "31.4% in Q4 2025"
    pattern = r"(Q[1-4])\s+(\d{4})[^\d]{0,20}?(\d+\.?\d*)\s*%"
    rows = []
    for q, year, rate in re.findall(pattern, html, re.IGNORECASE):
        month = _QUARTERS.get(q.upper())
        if month:
            rows.append((_quarter_end(int(year), month), rate))

    # Also try "31.4% in Q4 2025" pattern
    pattern2 = r"(\d+\.?\d*)\s*%[^<]{0,20}?in\s+(Q[1-4])\s+(\d{4})"
    for rate, q, year in re.findall(pattern2, html, re.IGNORECASE):
        month = _QUARTERS.get(q.upper())
        if month:
            rows.append((_quarter_end(int(year), month), rate))

    rows = sorted(set(rows))
    return rows[-4:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.statssa.gov.za/ → P0211 Quarterly Labour Force Survey manually")
