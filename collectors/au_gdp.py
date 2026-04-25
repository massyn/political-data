"""AU GDP Growth (quarterly QoQ%) — ABS National Accounts latest release HTML.

Source: https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release

Returns (date, qoq_pct) for the most recent quarter.
Released approximately: March (Dec qtr), June (Mar qtr), Sep (Jun qtr), Dec (Sep qtr).

FRAGILE: ABS page structure changes break this scraper. If it fails, visit the
ABS page above and update data.csv manually.
"""

import re
import urllib.request


_QUARTER_END = {"march": "03-31", "june": "06-30", "september": "09-30", "december": "12-31"}


def collect() -> list[tuple]:
    url = "https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # "rose 0.8% in the [quarter] to [Month] quarter [Year]"
    # or "rose 0.8% in seasonally adjusted... December 2025"
    pattern = r"(?:rose|fell|grew|contracted|expanded)[^<]{0,60}?(\d+\.?\d*)%[^<]{0,80}?(january|february|march|april|may|june|july|august|september|october|november|december)[^<]{0,20}?(\d{4})"
    m = re.search(pattern, html, re.IGNORECASE)
    if not m:
        return []

    val, month, year = m.group(1), m.group(2).lower(), int(m.group(3))
    # Convert month to quarter end
    qmap = {"march": "03-31", "june": "06-30", "september": "09-30", "december": "12-31",
            "january": "03-31", "february": "03-31", "april": "06-30", "may": "06-30",
            "july": "09-30", "august": "09-30", "october": "12-31", "november": "12-31"}
    q_end = qmap.get(month)
    if not q_end:
        return []
    return [(f"{year}-{q_end}", val)]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release")
