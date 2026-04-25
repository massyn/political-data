"""US CPI (quarterly) — BLS API series CUSR0000SA0.

Takes end-of-quarter monthly values and computes year-over-year percentage change.
Returns (date, yoy_pct, index_value) tuples for Q1-Q4 of recent years.
"""

import calendar
import json
import urllib.request
from collections import defaultdict


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/CUSR0000SA0"
    req = urllib.request.Request(url, headers={"User-Agent": "political-data-collector/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())

    # Build month -> index map
    by_month: dict[tuple[int, int], float] = {}
    for item in data["Results"]["series"][0]["data"]:
        p = item["period"]
        if not p.startswith("M") or p == "M13":
            continue
        by_month[(int(item["year"]), int(p[1:]))] = float(item["value"])

    # Quarter end months: March (3), June (6), September (9), December (12)
    rows = []
    for (year, month), index in sorted(by_month.items()):
        if month not in (3, 6, 9, 12):
            continue
        prior = by_month.get((year - 1, month))
        if prior is None:
            continue
        yoy = round((index - prior) / prior * 100, 2)
        rows.append((_month_end(year, month), str(yoy), str(round(index, 1))))

    return rows[-8:]


if __name__ == "__main__":
    for row in collect():
        print("\t".join(row))
