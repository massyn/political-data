"""
world_events.py - world events (pandemics, wars, crises) shown on charts.

Events live in world.yaml. For each chart we keep the events that overlap the
chart's date range and clip them to it, ready for the template to draw.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

WORLD_FILE = "world.yaml"


def load_events(path: str = WORLD_FILE) -> list[dict]:
    """Events from world.yaml, sorted by start date. Raises on a malformed entry."""
    if not Path(path).exists():
        return []
    raw = (yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}).get("events", [])
    events = []
    for entry in raw:
        missing = [k for k in ("name", "start", "colour") if not entry.get(k)]
        if missing:
            raise ValueError(f"{path}: event {entry.get('name', entry)!r} is missing {', '.join(missing)}")
        events.append({
            "name":   entry["name"],
            "icon":   entry.get("icon", ""),
            "start":  str(entry["start"]),
            "end":    str(entry["end"]) if entry.get("end") else None,
            "colour": entry["colour"],
        })
    return sorted(events, key=lambda e: e["start"])


def events_for_range(events: list[dict], first: str, last: str) -> list[dict]:
    """Events overlapping [first, last], with start/end clipped to the range.

    An event with no end date is ongoing and runs to the end of the range.
    `label` is the human-readable date span for the legend.
    """
    result = []
    for e in events:
        end = e["end"] or last
        if e["start"] > last or end < first:
            continue
        result.append({
            **e,
            "start": max(e["start"], first),
            "end":   min(end, last),
            "label": f"{_month(e['start'])} - {_month(e['end']) if e['end'] else 'ongoing'}",
        })
    return result


def _month(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%b %Y")
