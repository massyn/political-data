"""AU RBA Cash Rate Target (per decision date, %) — RBA statistics page HTML.

Source: https://www.rba.gov.au/statistics/cash-rate/

Scrapes the RBA cash rate table which lists each board decision date and the
resulting cash rate. Returns all decisions from the last 24 months.

Dates are recorded as the actual RBA board decision date (not end-of-month).
"""

import re
import urllib.request


_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def collect() -> list[tuple]:
    url = "https://www.rba.gov.au/statistics/cash-rate/"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="ignore")

    # Table rows contain: "19 Mar 2026" and "4.10" in adjacent cells
    # Match date strings like "4 Feb 2026" or "18 Mar 2026"
    date_pat  = r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})"
    rate_pat  = r"(\d+\.\d+)"

    # Find all date + rate pairs in sequence from the table
    combined  = re.findall(rf"{date_pat}.*?{rate_pat}", html, re.DOTALL)
    rows = []
    seen = set()
    for day, mon, year, rate in combined:
        month = _MONTHS.get(mon.lower())
        if not month:
            continue
        date_str = f"{int(year)}-{month:02d}-{int(day):02d}"
        if date_str not in seen:
            seen.add(date_str)
            rows.append((date_str, rate))

    rows.sort()
    return rows[-24:] if rows else []


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows:
            print("\t".join(row))
    else:
        print("No data — check https://www.rba.gov.au/statistics/cash-rate/ manually")
