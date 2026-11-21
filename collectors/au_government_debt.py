"""AU Government Debt (monthly, AUD billion) - AOFM Data Hub, portfolio aggregate.

Source: https://aofm.gov.au/data-hub  ("Portfolio aggregate - settlement")

The workbook's FaceValue sheet has one row per month-end. The figure used is the
"Total AUD Main Funding Instruments" liability: Treasury Bonds, Treasury Indexed
Bonds (capital indexed) and Treasury Notes at face value, i.e. Australian
Government Securities on issue. The file is replaced in place each month, so the
URL is stable.
"""

import io
import logging
import time
import urllib.error
import urllib.request
from datetime import datetime

import openpyxl

_URL = (
    "https://www.aofm.gov.au/sites/default/files/2025-05-02/"
    "portfolio_aggregate_-_settlement.xlsx"
)
_SHEET = "FaceValue"
_COLUMN = "Total AUD Main Funding Instruments"

# Plausible bounds (AUD billion) to reject a mis-parsed column or unit change.
_ATTEMPTS = 3
_TIMEOUT = 30
_BACKOFF = 5

log = logging.getLogger(__name__)

_MIN_BN = 10
_MAX_BN = 5_000


def _download() -> bytes:
    """Fetch the workbook, retrying transient network failures."""
    req = urllib.request.Request(_URL, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(1, _ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                return r.read()
        except (TimeoutError, urllib.error.URLError) as exc:
            log.warning("AOFM download attempt %d/%d failed: %s", attempt, _ATTEMPTS, exc)
            if attempt == _ATTEMPTS:
                raise
            time.sleep(_BACKOFF * attempt)


def collect() -> list[tuple]:
    payload = _download()

    ws = openpyxl.load_workbook(io.BytesIO(payload), read_only=True, data_only=True)[_SHEET]
    rows = list(ws.iter_rows(values_only=True))

    col = next(
        (i for row in rows if row and row[0] == "Instrument"
         for i, name in enumerate(row) if name == _COLUMN),
        None,
    )
    if col is None:
        return []

    result = []
    for row in rows:
        if not isinstance(row[0], datetime) or not isinstance(row[col], (int, float)):
            continue
        billions = round(abs(row[col]) / 1e9, 1)
        if _MIN_BN <= billions <= _MAX_BN:
            result.append((row[0].date().isoformat(), billions))
    return result


if __name__ == "__main__":
    rows = collect()
    if rows:
        for row in rows[-12:]:
            print("\t".join(str(c) for c in row))
    else:
        print(f"No data - check {_URL}")
