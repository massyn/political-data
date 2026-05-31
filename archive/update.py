"""
update.py — refresh all stale indicators by running their collectors.

Usage:
    python update.py                    # update all stale indicators
    python update.py --dry-run          # show what would change, no writes
    python update.py --force            # update all indicators regardless of staleness
    python update.py unemployment_rate  # target a specific indicator by name
"""

import csv
import importlib.util
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

STALE_DAYS = {
    "Month":   42,
    "Quarter": 120,
    "Annual":  400,
    "3 Year":  1280,
}


def is_stale(last_updated: str | None, frequency: str) -> bool:
    if not last_updated:
        return True
    lu = date.fromisoformat(str(last_updated))
    return (date.today() - lu).days > STALE_DAYS.get(frequency, 90)


def existing_dates(csv_path: Path) -> set[str]:
    with open(csv_path, newline="") as f:
        return {row["date"] for row in csv.DictReader(f)}


def append_rows(csv_path: Path, rows: list[tuple]) -> None:
    with open(csv_path, "a", newline="") as f:
        csv.writer(f).writerows(rows)


def update_last_updated(yaml_path: Path, new_date: str) -> None:
    text = yaml_path.read_text()
    text = re.sub(r"^last_updated:.*$", f"last_updated: {new_date}", text, flags=re.MULTILINE)
    yaml_path.write_text(text)


def run_collector(path: str) -> list[tuple]:
    spec = importlib.util.spec_from_file_location("_col", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.collect()


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    force   = "--force"   in sys.argv
    target  = next((a for a in sys.argv[1:] if not a.startswith("--")), None)

    updated, needs_manual, already_current = [], [], []

    for yaml_path in sorted(Path("data").glob("*/*/indicator.yaml")):
        ind          = yaml.safe_load(yaml_path.read_text())
        jurisdiction = yaml_path.parts[-3]
        name         = yaml_path.parts[-2]
        label        = f"{jurisdiction}/{name}"

        if target and target not in name:
            continue

        frequency    = ind.get("frequency", "Month")
        last_updated = str(ind["last_updated"]) if ind.get("last_updated") else None
        collector    = ind.get("collector")
        stale        = force or is_stale(last_updated, frequency)

        if not stale:
            already_current.append(label)
            continue

        if not collector:
            needs_manual.append(f"{label}  (last: {last_updated or 'never'})")
            continue

        print(f"  {label} ...", end=" ", flush=True)
        try:
            rows = run_collector(collector)
        except Exception as exc:
            print(f"FAILED — {exc}")
            needs_manual.append(f"{label}  (collector error: {exc})")
            continue

        if not rows:
            print("no data returned")
            needs_manual.append(f"{label}  (collector returned nothing)")
            continue

        csv_path = yaml_path.parent / "data.csv"
        known    = existing_dates(csv_path)
        new_rows = sorted(r for r in rows if r[0] not in known)

        if not new_rows:
            print("already up to date")
            already_current.append(label)
            continue

        latest = new_rows[-1][0]
        print(f"adding {len(new_rows)} row(s) through {latest}")

        if not dry_run:
            append_rows(csv_path, new_rows)
            update_last_updated(yaml_path, latest)

        updated.append(f"{label} → {latest}")

    # ── summary ──────────────────────────────────────────────────────────────
    print()
    if updated:
        print(f"Updated ({len(updated)}):")
        for u in updated:
            print(f"  ✓ {u}")

    if needs_manual:
        print(f"\nManual update required ({len(needs_manual)}):")
        for m in needs_manual:
            print(f"  • {m}")

    if not updated and not needs_manual:
        print("All indicators are current.")

    if updated and not dry_run:
        print("\nValidating...")
        subprocess.run([sys.executable, "data.py"], check=True)


if __name__ == "__main__":
    main()
