"""Shared fetch helper for the ABS Data API (SDMX), used by the au_* collectors.

API: https://data.api.abs.gov.au/rest/data/ABS,<dataflow>,<version>/<key>
Collectors import this as `from collectors.abs_api import fetch`; run a
collector directly with `python -m collectors.<name>` from the project root.
"""

import calendar
import csv
import io

from collectors.net import get

_BASE = "https://data.api.abs.gov.au/rest/data"


def _period_end(period: str) -> str:
    """'2026-Q3' -> '2026-09-30'; '2026-10' -> '2026-10-31'."""
    year, rest = period.split("-", 1)
    month = int(rest[1]) * 3 if rest.startswith("Q") else int(rest)
    return f"{year}-{month:02d}-{calendar.monthrange(int(year), month)[1]:02d}"


def fetch(dataflow: str, key: str) -> list[tuple[str, float]]:
    """[(period_end_date, value)] ascending, for one fully specified series key."""
    text = get(f"{_BASE}/ABS,{dataflow}/{key}", headers={"Accept": "text/csv"}).decode("utf-8")

    if text.startswith("NoRecordsFound") or not text.strip():
        return []
    rows = {
        _period_end(r["TIME_PERIOD"]): float(r["OBS_VALUE"])
        for r in csv.DictReader(io.StringIO(text))
        if r.get("OBS_VALUE")
    }
    return sorted(rows.items())


def annual_change(series: list[tuple[str, float]], lag: int) -> dict[str, float]:
    """{date: % change versus `lag` observations earlier} from a level series."""
    return {
        series[i][0]: (series[i][1] / series[i - lag][1] - 1) * 100
        for i in range(lag, len(series))
    }
