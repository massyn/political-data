"""AU Wage Price Index (quarterly) — ABS WPI latest release HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release

Returns (date, annual_growth_pct, index_value). Index uses 2008-09 = 100 base.
Released approximately: February (Dec qtr), May (Mar qtr), August (Jun qtr), November (Sep qtr).

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and update data.csv manually.
"""

import re
import urllib.request


_QUARTER_MAP = {
    "march": "03-31", "june": "06-30", "september": "09-30", "december": "12-31",
}


def collect() -> list[tuple]:
    url = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # "rose 3.4% over the twelve months to the December quarter"
    annual_m = re.search(r"(?:rose|increased|grew)[^<]{0,60}?(\d+\.?\d*)%[^<]{0,60}?twelve months", html, re.IGNORECASE)
    qtr_m    = re.search(r"(march|june|september|december)\s+quarter[,\s]+(\d{4})", html, re.IGNORECASE)
    idx_m    = re.search(r"index[^\d]{0,30}?(\d{3}\.\d)", html, re.IGNORECASE)

    if not annual_m or not qtr_m:
        return []

    annual = annual_m.group(1)
    qend   = _QUARTER_MAP.get(qtr_m.group(1).lower(), "")
    year   = qtr_m.group(2)
    index  = idx_m.group(1) if idx_m else ""

    if not qend:
        return []
    return [(f"{year}-{qend}", annual, index)] if index else [(f"{year}-{qend}", annual, "")]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(r for r in row if r))
    else:
        print("No data — check https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release")
