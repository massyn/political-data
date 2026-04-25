"""AU Unemployment Rate (monthly, %) — ABS Labour Force latest release HTML.

Source: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release

Scrapes the seasonally adjusted unemployment rate and reference month from the
ABS Labour Force release page. Returns the most recent 1-2 months.

FRAGILE: ABS page structure changes break this scraper. If it fails, get the
latest rate from the ABS page above and add a row manually to data.csv.
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
    url = "https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Find "unemployment rate [rose/fell/remained at] X.X% in [Month] [Year]"
    pattern = r"unemployment rate[^<]{0,60}?(\d+\.\d+)%[^<]{0,60}?in\s+(\w+)\s+(\d{4})"
    matches = re.findall(pattern, html, re.IGNORECASE)
    rows = []
    for rate, month_name, year in matches:
        month = _MONTHS.get(month_name.lower())
        if month:
            rows.append((_month_end(int(year), month), rate))
    rows = sorted(set(rows))
    return rows[-2:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release")
