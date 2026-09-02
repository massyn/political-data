"""AU Median House Price (quarterly, AUD) — ABS Total Value of Dwellings HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release

NOTE: The ABS publication reports MEAN dwelling price (not median). This series
tracks the mean price across the eight capital cities as a proxy; the indicator
title uses "median" for public familiarity but the underlying figure is the mean.

The release headline sentence reads, e.g.:
    "The mean price of residential dwellings rose by $22,300 to $1,111,100 this quarter."
and the release quarter appears as "March quarter 2026". Both are parsed from the
rendered HTML text.

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and update the indicator YAML manually.
"""

import re
import urllib.request

_URL = (
    "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/"
    "total-value-dwellings/latest-release"
)

_QUARTER_END = {
    "march": "03-31",
    "june": "06-30",
    "september": "09-30",
    "december": "12-31",
}

# Plausible bounds for an Australian mean dwelling price (AUD). Guards against the
# scraper latching onto an unrelated dollar figure on the page (e.g. the total
# value of the dwelling stock, quoted in billions).
_MIN_PRICE = 200_000
_MAX_PRICE = 5_000_000


def collect() -> list[tuple]:
    req = urllib.request.Request(
        _URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    price_m = re.search(
        r"mean price of residential dwellings (?:rose|fell|increased|decreased|was)"
        r"[^.]*?\bto \$\s*([\d,]+)",
        text,
        re.IGNORECASE,
    )
    qtr_m = re.search(
        r"(March|June|September|December) quarter (\d{4})",
        text,
        re.IGNORECASE,
    )
    if not price_m or not qtr_m:
        return []

    price = int(price_m.group(1).replace(",", ""))
    if not _MIN_PRICE <= price <= _MAX_PRICE:
        return []

    qend = _QUARTER_END[qtr_m.group(1).lower()]
    year = qtr_m.group(2)
    return [(f"{year}-{qend}", str(price))]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print(f"No data — check {_URL}")
