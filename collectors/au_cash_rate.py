"""AU RBA Cash Rate Target (per decision date, %) — RBA statistics page HTML.

Source: https://www.rba.gov.au/statistics/cash-rate/

The RBA table lists one row per board decision:

    <date>        <change>     <new level>
    12 Aug 2026   0.00         4.35
    6 May 2026    +0.25        4.35
    13 Aug 2025   -0.25        3.60

Returns (decision_date, new_level) for the last 24 decisions. The date is the
actual board decision date, not end-of-month.

IMPORTANT: read the SECOND number in each row (the resulting cash rate level),
not the first (the change in basis points). An earlier version of this collector
scraped the change column and polluted the series with 0.00 / 0.25 values.

NOTE: rba.gov.au blocks the WebFetch tool (HTTP 403) but serves plain
urllib requests. Its TLS chain is not trusted by Python on Windows, so an
unverified SSL context is used — acceptable for a read-only public data scrape.

FRAGILE: RBA page structure changes break this scraper. If it fails, read the
latest decision from the source URL (or a news report of the RBA decision) and
add a row manually.
"""

import re
import ssl
import urllib.request

_URL = "https://www.rba.gov.au/statistics/cash-rate/"

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Plausible bounds for the cash rate level, to reject a row where only the
# change column was captured (0.00 / 0.25) or a stray number was matched.
_MIN_RATE = 0.05
_MAX_RATE = 20.0


def collect() -> list[tuple]:
    req = urllib.request.Request(_URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        html = r.read().decode("utf-8", errors="ignore")

    rows: list[tuple[str, str]] = []
    seen: set[str] = set()

    for tr in re.findall(r"<tr[^>]*>.*?</tr>", html, re.DOTALL):
        text = re.sub(r"<[^>]+>", " ", tr)
        text = re.sub(r"\s+", " ", text).strip()

        date_m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\b", text)
        if not date_m:
            continue
        month = _MONTHS.get(date_m.group(2).lower())
        if month is None:
            continue

        # Numbers after the date: [change, new_level, ...]. Take the level.
        tail = text[date_m.end():]
        nums = re.findall(r"[-+]?\d+\.\d{1,2}", tail)
        if len(nums) < 2:
            continue
        try:
            level = float(nums[1])
        except ValueError:
            continue
        if not _MIN_RATE <= level <= _MAX_RATE:
            continue

        date_str = f"{int(date_m.group(3))}-{month:02d}-{int(date_m.group(1)):02d}"
        if date_str in seen:
            continue
        seen.add(date_str)
        rows.append((date_str, f"{level:g}"))

    rows.sort()
    return rows[-24:]


if __name__ == "__main__":
    result = collect()
    if result:
        for row in result:
            print("\t".join(row))
    else:
        print(f"No data — check {_URL} manually")
