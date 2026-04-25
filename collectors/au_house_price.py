"""AU Median House Price (quarterly, AUD) — ABS Total Value of Dwellings HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release

NOTE: The ABS publication reports MEAN dwelling price (not median). This series
tracks the mean price as a proxy; the indicator description should reflect this.
The page does not expose the median price in the main HTML — it is in a
downloadable Excel table. This collector returns the mean price from the page.

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and update data.csv manually.
"""

import re
import urllib.request


_QUARTER_MAP = {
    "march": "03-31", "june": "06-30", "september": "09-30", "december": "12-31",
}


def collect() -> list[tuple]:
    url = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Look for "$X,XXX,XXX" or "$X.XXX" million pattern + quarter
    price_m = re.search(r"\$\s*(\d[\d,]+)", html)
    qtr_m   = re.search(r"(march|june|september|december)\s+(?:quarter\s+)?(\d{4})", html, re.IGNORECASE)

    if not price_m or not qtr_m:
        return []

    # Strip commas; convert to integer
    price = price_m.group(1).replace(",", "")
    if len(price) < 5:
        price = str(int(float(price) * 1_000_000))

    qend = _QUARTER_MAP.get(qtr_m.group(1).lower(), "")
    year = qtr_m.group(2)
    if not qend:
        return []
    return [(f"{year}-{qend}", price)]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release")
