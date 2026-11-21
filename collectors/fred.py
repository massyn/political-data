"""Shared fetch helper for FRED monthly series (no API key: the public CSV download).

https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>
Collectors import it as `from collectors.fred import monthly`.
"""

import calendar
import csv
import io
from datetime import date

from collectors.net import get

_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"


def monthly(series: str) -> list[tuple[str, float]]:
    """[(month_end_date, value)] ascending. FRED dates months by their first day; the
    current month is dropped because its average is still being built."""
    # FRED stalls requests that send a custom User-Agent, so use urllib's default.
    text = get(_URL.format(series=series), user_agent=None).decode("utf-8")
    today = date.today()
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        value = r.get(series, "").strip()
        if not value or value == ".":
            continue
        first = date.fromisoformat(r["observation_date"])
        if (first.year, first.month) >= (today.year, today.month):
            continue
        rows.append((f"{first.year}-{first.month:02d}-{calendar.monthrange(first.year, first.month)[1]:02d}", float(value)))
    return sorted(rows)
