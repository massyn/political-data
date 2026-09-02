"""AU Consumer Price Index (quarterly YoY) — ABS CPI latest release HTML.

Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release

Returns (date, yoy_pct) for the most recent quarter-end month, where
Q1 = March 31, Q2 = June 30, Q3 = September 30, Q4 = December 31.

The ABS now publishes a complete MONTHLY CPI. Its release page carries a
"monthly and annual movement (%)" table of rows shaped "<Mon>-<YY> <monthly>
<annual>". This collector reads that table, keeps the rows whose month is a
quarter end, and emits the latest one so the existing quarterly series stays on
a quarterly cadence.

The CPI index-value series (the second graph in the indicator YAML, base
2011-12 = 100) is deliberately NOT emitted: the ABS rebased monthly CPI
reporting to September 2025 = 100 and no longer publishes on the old base, so
extending that series needs an explicit decision. A two-element row leaves the
index graph untouched (see Indicator.merge in update.py).

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and read the annual movement for the latest quarter manually.
"""

import re
import urllib.request

_URL = (
    "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/"
    "consumer-price-index-australia/latest-release"
)

_MONTH_NUM = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_QUARTER_END = {3: "03-31", 6: "06-30", 9: "09-30", 12: "12-31"}


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

    # Rows carrying BOTH a monthly and an annual movement, e.g. "Jun-26 -0.1 3.8".
    # Rows with only a monthly figure (the first 11 months of any series) are skipped.
    rows: list[tuple[int, int, str]] = []
    for m in re.finditer(
        r"\b([A-Z][a-z]{2})-(\d{2})\s+(-?\d+\.\d)\s+(-?\d+\.\d)\b", text
    ):
        month = _MONTH_NUM.get(m.group(1).lower())
        if month is None:
            continue
        year = 2000 + int(m.group(2))
        annual = m.group(4)
        rows.append((year, month, annual))

    quarter_rows = [r for r in rows if r[1] in _QUARTER_END]
    if not quarter_rows:
        return []

    year, month, annual = max(quarter_rows, key=lambda r: (r[0], r[1]))
    return [(f"{year}-{_QUARTER_END[month]}", annual)]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print(f"No data — check {_URL}")
