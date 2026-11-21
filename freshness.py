"""
freshness.py - how overdue an indicator is, measured in frequency cycles.

The next observation is due one cycle after the latest one (a month, quarter,
year or three years). Once today passes that due date:
    overdue by up to one cycle   -> "stale"
    overdue by more than a cycle -> "out_of_date"
Anything not yet overdue is "current".
"""

from __future__ import annotations

import calendar
from datetime import date

CYCLE_MONTHS: dict[str, int] = {"Month": 1, "Quarter": 3, "Annual": 12, "3 Year": 36}

LABELS = {"current": "Up to date", "stale": "Stale", "out_of_date": "Out of date"}


def add_months(d: date, months: int) -> date:
    """d plus whole months; month-end dates stay month-end (30 Jun + 3 -> 30 Sep)."""
    index = d.year * 12 + d.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    last_day = calendar.monthrange(year, month)[1]
    is_month_end = d.day == calendar.monthrange(d.year, d.month)[1]
    return date(year, month, last_day if is_month_end else min(d.day, last_day))


def freshness(latest: date | None, frequency: str, today: date | None = None) -> dict:
    """{status, label, due, overdue_days} for the latest observation date."""
    if latest is None or frequency not in CYCLE_MONTHS:
        return {"status": "out_of_date", "label": LABELS["out_of_date"], "due": None, "overdue_days": None}

    today = today or date.today()
    months = CYCLE_MONTHS[frequency]
    due = add_months(latest, months)
    overdue = (today - due).days
    cycle_days = (add_months(due, months) - due).days

    if overdue <= 0:
        status = "current"
    elif overdue <= cycle_days:
        status = "stale"
    else:
        status = "out_of_date"
    return {
        "status": status, "label": LABELS[status],
        "due": due.isoformat(), "overdue_days": max(overdue, 0),
    }
