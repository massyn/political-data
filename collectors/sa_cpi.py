"""SA Consumer Price Index (quarterly) — Trading Economics HTML scrape + index calculation.

Source: https://tradingeconomics.com/south-africa/inflation-cpi

Returns (date, yoy_pct, index_value) for end-of-quarter months.

INDEX CALCULATION NOTE: Trading Economics reports the CPI index using a different
base period (~2021=100, ~104 range) than our data file (Dec 2016=100, ~160 range).
This collector calculates the index by compounding: prior_year_index * (1 + rate/100),
where prior_year_index is read from the existing data.csv. This is an approximation.

For the precise StatsSA CPI index (December 2016=100), visit:
  https://www.statssa.gov.za/?page_id=1871
and look for the CPI Historical Table Archive. Update data.csv manually if needed.

FRAGILE: Trading Economics may block automated requests.
"""

import calendar
import csv
import re
import urllib.request
from pathlib import Path


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}
_QUARTER_MONTHS = {3, 6, 9, 12}


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def _load_prior_index(month: int, year: int) -> float | None:
    csv_path = Path("data/South Africa/consumer_price_index/data.csv")
    prior_date = _month_end(year - 1, month)
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            if row["date"] == prior_date:
                return float(row["index"])
    return None


def collect() -> list[tuple]:
    url = "https://tradingeconomics.com/south-africa/inflation-cpi"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Pattern: "3.1% in March of 2026" or "edged up to 3.1% in March 2026"
    pattern = r"(\d+\.?\d*)\s*%[^<]{0,30}?in\s+(\w+)[^\d]{0,10}?(?:of\s+)?(\d{4})"
    rows = []
    for rate, month_name, year in re.findall(pattern, html, re.IGNORECASE):
        month = _MONTHS.get(month_name.lower())
        if not month or month not in _QUARTER_MONTHS:
            continue
        year_int = int(year)
        prior_idx = _load_prior_index(month, year_int)
        if prior_idx is None:
            continue
        index = round(prior_idx * (1 + float(rate) / 100), 4)
        rows.append((_month_end(year_int, month), rate, str(index)))
    rows = sorted(set(rows))
    return rows[-4:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.statssa.gov.za/?page_id=1871 manually")
