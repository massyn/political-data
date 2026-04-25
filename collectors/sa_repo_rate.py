"""SA SARB Repo Rate (per decision date, %) — Trading Economics HTML scrape.

Source: https://tradingeconomics.com/south-africa/interest-rate

The SARB MPC meets approximately 6 times per year (every two months). Decisions
are recorded on the end-of-month date of the meeting month for consistency with
existing data (e.g., a March 26 decision is recorded as 2026-03-31).

FRAGILE: Trading Economics may block automated requests. If this fails, check:
  https://www.resbank.co.za/en/home/what-we-do/monetary-policy
and add the decision date and rate to data.csv manually.
"""

import calendar
import re
import urllib.request


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://tradingeconomics.com/south-africa/interest-rate"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Pattern: "November 20, 2025 | 6.75% | Cut of 25 basis points"
    # or "January 29, 2026 | 6.75% | Held unchanged"
    pattern = r"(\w+)\s+\d+,\s+(\d{4})[^\d]{0,20}?(\d+\.\d+)\s*%"
    rows = []
    for month_name, year, rate in re.findall(pattern, html, re.IGNORECASE):
        month = _MONTHS.get(month_name.lower())
        if month:
            rows.append((_month_end(int(year), month), rate))
    rows = sorted(set(rows))
    return rows[-6:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.resbank.co.za/en/home/what-we-do/monetary-policy manually")
