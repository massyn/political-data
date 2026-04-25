"""US Unemployment Rate — BLS API series LNS14000000 (UNRATE)."""

import calendar
import json
import urllib.request


def _month_end(year: int, month: int) -> str:
    return f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


def collect() -> list[tuple]:
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/LNS14000000"
    req = urllib.request.Request(url, headers={"User-Agent": "political-data-collector/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    rows = []
    for item in data["Results"]["series"][0]["data"]:
        p = item["period"]
        if not p.startswith("M") or p == "M13":
            continue
        rows.append((_month_end(int(item["year"]), int(p[1:])), item["value"]))
    rows.sort()
    return rows[-12:]


if __name__ == "__main__":
    for row in collect():
        print("\t".join(row))
