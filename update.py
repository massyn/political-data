"""
update.py — indicator refresh runner for the data schema.

Usage:
    python update.py                 # update all stale indicators
    python update.py --dry-run       # preview changes, no writes
    python update.py --force         # update all regardless of staleness
    python update.py cpi             # target a specific indicator by id substring
"""

from __future__ import annotations

import importlib.util
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

STALE_DAYS: dict[str, int] = {
    "Month":   42,
    "Quarter": 120,
    "Annual":  400,
    "3 Year":  1280,
}


# ── YAML I/O ─────────────────────────────────────────────────────────────────

def _normalise_date_keys(obj: Any) -> Any:
    """Recursively convert datetime.date keys (produced by PyYAML) to ISO strings."""
    if isinstance(obj, dict):
        return {
            (k.isoformat() if isinstance(k, date) else k): _normalise_date_keys(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_normalise_date_keys(i) for i in obj]
    return obj


def _to_date_keys(obj: Any) -> Any:
    """Recursively convert ISO date string keys back to datetime.date for clean YAML output."""
    if isinstance(obj, dict):
        result: dict = {}
        for k, v in obj.items():
            if isinstance(k, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", k):
                k = date.fromisoformat(k)
            result[k] = _to_date_keys(v)
        return result
    if isinstance(obj, list):
        return [_to_date_keys(i) for i in obj]
    return obj


def _coerce(val: Any) -> Any:
    """Convert a string value to float if possible, otherwise leave unchanged."""
    if not isinstance(val, str):
        return val
    try:
        return float(val)
    except (ValueError, TypeError):
        return val


def _load(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _normalise_date_keys(raw)


def _save(path: Path, data: dict) -> None:
    path.write_text(
        yaml.dump(
            _to_date_keys(data),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        ),
        encoding="utf-8",
    )


# ── Indicator ─────────────────────────────────────────────────────────────────

class Indicator:
    STATUS_CURRENT         = "current"
    STATUS_STALE_COLLECTOR = "stale:collector"
    STATUS_STALE_MANUAL    = "stale:manual"

    def __init__(self, path: Path) -> None:
        self.path = path
        self._data = _load(path)

    # ── identity ─────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def jurisdiction(self) -> str:
        return self._data["jurisdiction"]

    @property
    def title(self) -> str:
        return self._data["title"]

    @property
    def label(self) -> str:
        return f"{self.jurisdiction} / {self.title}"

    # ── schedule ─────────────────────────────────────────────────────────────

    @property
    def category(self) -> str:
        return self._data.get("category", "")

    @property
    def frequency(self) -> str:
        return self._data["frequency"]

    @property
    def last_updated(self) -> date | None:
        v = self._data.get("last_updated")
        if not v:
            return None
        return v if isinstance(v, date) else date.fromisoformat(str(v))

    @property
    def days_since_update(self) -> int | None:
        return (date.today() - self.last_updated).days if self.last_updated else None

    @property
    def is_stale(self) -> bool:
        if not self.last_updated:
            return True
        threshold = STALE_DAYS.get(self.frequency, 90)
        return (date.today() - self.last_updated).days > threshold

    # ── graph structure ───────────────────────────────────────────────────────

    @property
    def graphs(self) -> list[dict]:
        g = self._data.get("graph", [])
        return g if isinstance(g, list) else []

    @property
    def chart_graphs(self) -> list[dict]:
        """Graph entries that are rendered as charts (have x/y axis fields)."""
        return [g for g in self.graphs if "x" in g]

    @property
    def is_overlay(self) -> bool:
        """True for government/reference indicators — data used only as chart overlays."""
        return bool(self.graphs) and "x" not in self.graphs[0]

    # ── collector ─────────────────────────────────────────────────────────────

    @property
    def collector(self) -> str | None:
        return self._data.get("collector")

    @property
    def status(self) -> str:
        if not self.is_stale:
            return self.STATUS_CURRENT
        return self.STATUS_STALE_COLLECTOR if self.collector else self.STATUS_STALE_MANUAL

    def collect(self) -> list[tuple]:
        if not self.collector:
            raise RuntimeError(f"{self.id}: no collector configured")
        spec = importlib.util.spec_from_file_location("_col", self.collector)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.collect()

    # ── data access ───────────────────────────────────────────────────────────

    def known_dates(self) -> set[str]:
        """Dates already present in the first chart graph's data."""
        cg = self.chart_graphs
        if not cg:
            return set()
        return set(cg[0].get("data", {}).keys())

    # ── merge & persist ───────────────────────────────────────────────────────

    def merge(self, rows: list[tuple]) -> int:
        """
        Merge collector rows into chart graph data. Returns count of new rows added.

        Row format: (date_str, val_for_graph0[, val_for_graph1, ...])
        Column index i+1 maps to chart_graphs[i].
        Overlay graphs (no 'x' key) are skipped — they are manually maintained.
        """
        cg = self.chart_graphs
        if not cg:
            return 0

        known = self.known_dates()
        new_rows = sorted(r for r in rows if r[0] not in known)
        if not new_rows:
            return 0

        for row in new_rows:
            d = row[0]
            for col_offset, graph in enumerate(cg):
                col_index = col_offset + 1
                if col_index < len(row):
                    graph.setdefault("data", {})[d] = _coerce(row[col_index])

        self._data["last_updated"] = date.fromisoformat(new_rows[-1][0])
        return len(new_rows)

    def save(self) -> None:
        _save(self.path, self._data)


# ── runner ────────────────────────────────────────────────────────────────────

def _run_indicator(ind: Indicator, dry_run: bool) -> tuple[str, str]:
    """
    Attempt to collect and merge data for a stale indicator.
    Returns (outcome, message) where outcome is 'updated', 'current', or 'error'.
    """
    try:
        rows = ind.collect()
    except Exception as exc:
        return "error", f"collector failed: {exc}"

    if not rows:
        return "error", "collector returned no data"

    if dry_run:
        new_count = sum(1 for r in rows if r[0] not in ind.known_dates())
        if new_count == 0:
            return "current", "already up to date"
        latest = sorted(r[0] for r in rows)[-1]
        return "updated", f"would add {new_count} row(s) through {latest}"

    added = ind.merge(rows)
    if added == 0:
        return "current", "already up to date"

    latest = sorted(r[0] for r in rows)[-1]
    ind.save()
    return "updated", f"added {added} row(s) through {latest}"


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    force   = "--force"   in sys.argv
    target  = next((a for a in sys.argv[1:] if not a.startswith("--")), None)

    updated: list[str] = []
    manual:  list[str] = []
    errors:  list[str] = []
    current: list[str] = []

    for yaml_path in sorted(Path("data").glob("*.yaml")):
        ind = Indicator(yaml_path)

        if target and target not in ind.id:
            continue

        stale = force or ind.is_stale
        days  = ind.days_since_update
        age   = f"{days}d ago" if days is not None else "never updated"

        if not stale:
            current.append(f"{ind.label}  ({age})")
            continue

        if ind.status == Indicator.STATUS_STALE_MANUAL:
            manual.append(f"{ind.label}  (last: {ind.last_updated or 'never'})")
            continue

        print(f"  {ind.label} ...", end=" ", flush=True)
        outcome, message = _run_indicator(ind, dry_run)
        print(message)

        if outcome == "updated":
            updated.append(f"{ind.label} -> {message}")
        elif outcome == "current":
            current.append(f"{ind.label}  ({age})")
        else:
            errors.append(f"{ind.label}: {message}")

    # ── summary ───────────────────────────────────────────────────────────────
    print()

    if updated:
        prefix = "[dry-run] would update" if dry_run else "Updated"
        print(f"{prefix} ({len(updated)}):")
        for u in updated:
            print(f"  + {u}")

    if manual:
        print(f"\nManual update required ({len(manual)}):")
        for m in manual:
            print(f"  . {m}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ! {e}")

    if not updated and not manual and not errors:
        print(f"All {len(current)} indicator(s) are current.")
    elif current and not (manual or errors):
        print(f"\n{len(current)} indicator(s) already current.")


if __name__ == "__main__":
    main()
