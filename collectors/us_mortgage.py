"""US 30-Year Mortgage Rate — Freddie Mac PMMS weekly archive.

Source: https://www.freddiemac.com/pmms/archive
Computes monthly average from weekly survey readings.
"""

import calendar
import re
import urllib.request
from collections import defaultdict


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://www.freddiemac.com/pmms/archive"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Weekly data rows: date like "01/02/2026" and rate like "6.91"
    pattern = r"(\d{2})/(\d{2})/(\d{4})[^<]*?(\d+\.\d+)%"
    weekly: dict[tuple[int, int], list[float]] = defaultdict(list)
    for month, _day, year, rate in re.findall(pattern, html):
        weekly[(int(year), int(month))].append(float(rate))

    if not weekly:
        return []

    rows = []
    for (year, month), rates in sorted(weekly.items()):
        avg = round(sum(rates) / len(rates), 2)
        rows.append((_month_end(year, month), str(avg)))

    return rows[-6:]


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.freddiemac.com/pmms/archive manually")
