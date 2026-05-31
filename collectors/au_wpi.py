"""AU Wage Price Index (quarterly, annual growth %) — ABS WPI latest release HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release

Returns (date, annual_growth_pct). Index value is no longer published on the
ABS summary page and must be updated manually from the full data download.

Page structure (as of 2026):
  "Over the twelve months to the {Quarter} quarter, the WPI rose {X.X}%."
  Quarter year appears elsewhere as "{Quarter} quarter {YYYY}" or
  "{Quarter} quarter, {YYYY}".

FRAGILE: ABS page wording changes break this scraper. If it fails, visit the
ABS page above and update the YAML manually.
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

    # Annual growth: "WPI rose 3.3%" — WPI is the anchor, not "twelve months"
    annual_m = re.search(
        r"WPI\s+(?:rose|increased|grew)\s+(\d+\.?\d*)%",
        html, re.IGNORECASE,
    )

    # Quarter + year: "March quarter, 2026" or "March quarter 2026"
    qtr_m = re.search(
        r"(march|june|september|december)\s+quarter[,\s]+(\d{4})",
        html, re.IGNORECASE,
    )

    if not annual_m or not qtr_m:
        return []

    annual = annual_m.group(1)
    qend = _QUARTER_MAP.get(qtr_m.group(1).lower(), "")
    year = qtr_m.group(2)
    if not qend:
        return []

    return [(f"{year}-{qend}", annual)]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(str(v) for v in row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release")
