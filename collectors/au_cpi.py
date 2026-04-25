"""AU Consumer Price Index (quarterly) — ABS CPI latest release HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release

Returns (date, yoy_pct, index_value) for the most recent quarter.
Q1 = March 31, Q2 = June 30, Q3 = September 30, Q4 = December 31.

Index uses 2011-12 = 100 base period.

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and update data.csv manually. The quarterly CPI is released in
late January, April, July, and October for the preceding quarter.
"""

import calendar
import re
import urllib.request


_QUARTER_END = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
_MONTHS_Q = {
    "march": 1, "june": 2, "september": 3, "december": 4,
    "mar": 1, "jun": 2, "sep": 3, "dec": 4,
}


def collect() -> list[tuple]:
    url = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Find annual rate like "rose 2.4%" and quarter like "December quarter 2025"
    rate_m = re.search(r"(?:rose|fell|increased|decreased)\s+(\d+\.?\d*)%", html, re.IGNORECASE)
    qtr_m  = re.search(r"(march|june|september|december)\s+quarter\s+(\d{4})", html, re.IGNORECASE)

    if not rate_m or not qtr_m:
        return []

    yoy  = rate_m.group(1)
    q    = _MONTHS_Q.get(qtr_m.group(1).lower())
    year = int(qtr_m.group(2))
    date_str = f"{year}-{_QUARTER_END[q]}"

    # Index value is harder to parse reliably — omit if not found
    idx_m = re.search(r"index[^\d]{0,30}?(\d{3}\.\d)", html, re.IGNORECASE)
    index = idx_m.group(1) if idx_m else ""

    return [(date_str, yoy, index)] if index else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release")
