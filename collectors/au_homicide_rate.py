"""AU Homicide Victimisation Rate (annual, victims per 100,000) - ABS Recorded Crime - Victims.

Source: https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-victims/latest-release

The latest-release page links the "Victims of crime, Australia (Tables 1 to 8)"
workbook. Table 1 holds the national series from 1993; the victimisation rate
block below the counts has a Homicide row (murder, attempted murder and
manslaughter, excluding driving causing death). Years are calendar years, so
each value is dated 31 December.

FRAGILE: relies on the workbook link text and Table 1 layout. If it fails, use
the workbook linked from the page above and add the row by hand.
"""

import io
import re
import urllib.request

import openpyxl

_PAGE = "https://www.abs.gov.au/statistics/people/crime-and-justice/recorded-crime-victims/latest-release"
_SITE = "https://www.abs.gov.au"
_TIMEOUT = 60


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def collect() -> list[tuple]:
    html = _get(_PAGE).decode("utf-8", errors="ignore")
    link = re.search(r'href="([^"]*Tables%201%20to%208[^"]*\.xlsx)"', html)
    if not link:
        return []

    ws = openpyxl.load_workbook(io.BytesIO(_get(_SITE + link.group(1))), read_only=True, data_only=True)["Table 1"]
    rows = list(ws.iter_rows(values_only=True))

    header = next((r for r in rows if r and r[0] == "Offence"), None)
    rate_start = next(
        (i for i, r in enumerate(rows) if any(str(c).startswith("Victimisation rate") for c in r if c)),
        None,
    )
    if header is None or rate_start is None:
        return []
    homicide = next((r for r in rows[rate_start:] if r and str(r[0]).startswith("Homicide")), None)
    if homicide is None:
        return []

    result = []
    for label, value in zip(header[1:], homicide[1:]):
        if label is None or not isinstance(value, (int, float)):
            continue
        result.append((f"{str(label)[:4]}-12-31", float(value)))
    return result


if __name__ == "__main__":
    rows = collect()
    if rows:
        print(f"{len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")
        for row in rows[-5:]:
            print("\t".join(str(c) for c in row))
    else:
        print(f"No data - check {_PAGE}")
