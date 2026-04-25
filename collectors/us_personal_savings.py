"""US Personal Savings Rate — BLS/BEA via Trading Economics HTML scrape.

Source: tradingeconomics.com/united-states/personal-savings
Returns the most recent 1-2 months of personal saving rate as % of disposable income.

FRAGILE: Trading Economics may block automated requests. If this collector fails,
visit https://fred.stlouisfed.org/series/PSAVERT for the latest value.
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
    url = "https://tradingeconomics.com/united-states/personal-savings"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Look for patterns like "decreased to 4 percent in February from 4.50 percent in January of 2026"
    pattern = r"(\d+(?:\.\d+)?)\s*percent\s+in\s+(\w+)\s+(?:from\s+\S+\s+in\s+\S+\s+)?of\s+(\d{4})"
    matches = re.findall(pattern, html, re.IGNORECASE)
    rows = []
    for value, month_name, year in matches:
        month = _MONTHS.get(month_name.lower())
        if month:
            rows.append((_month_end(int(year), month), value))
    rows = sorted(set(rows))
    return rows[-3:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://fred.stlouisfed.org/series/PSAVERT manually")
