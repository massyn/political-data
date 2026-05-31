"""AU Unemployment Rate (monthly, %) — ABS Labour Force latest release HTML.

Source: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release

Scrapes the seasonally adjusted unemployment rate and reference month from the
ABS Labour Force release page.

Page structure (as of 2026): "In seasonally adjusted terms, in {Month} {Year}:
the unemployment rate [increased/decreased/remained] ... to {X.X}%"

FRAGILE: ABS page wording changes break this scraper. If it fails, get the
latest rate from the ABS page above and add a row manually.
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

    # Month/year: "in April 2026" in key statistics section
    month_m = re.search(
        r"\bin\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
        html, re.IGNORECASE,
    )

    # Rate: "unemployment rate ... X.X%" — covers both "rose to X.X%" and "remained at X.X%"
    rate_m = re.search(r"unemployment rate[^<]{0,150}?(\d+\.\d+)%", html, re.IGNORECASE)

    if not month_m or not rate_m:
        return []

    month = _MONTHS.get(month_m.group(1).lower())
    year = int(month_m.group(2))
    if not month:
        return []

    return [(_month_end(year, month), rate_m.group(1))]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(str(v) for v in row))
    else:
        print("No data — check https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release")
