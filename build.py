"""
build.py — static site generator for the data indicator schema.

Usage:
    python build.py           # builds to ./dist
    python build.py ./out     # builds to ./out
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import jinja2
import yaml

from freshness import add_months, freshness
from world_events import events_for_range, load_events
from update import Indicator

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "./dist"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"
JURISDICTIONS_FILE = "jurisdictions.yaml"
LASTRUN_FILE = "lastrun.txt"
CHART_YEARS = 25


# ── helpers ───────────────────────────────────────────────────────────────────

def _cutoff() -> str:
    today = date.today()
    return f"{today.year - CHART_YEARS}-{today.month:02d}-{today.day:02d}"


def _sparkline(values: list[float], width: int = 140, height: int = 36) -> str:
    if len(values) < 2:
        return ""
    mn, mx = min(values), max(values)
    pad = 2
    if mx == mn:
        mid = height / 2
        pts = f"0,{mid:.0f} {width},{mid:.0f}"
    else:
        n = len(values) - 1
        pts = " ".join(
            f"{i / n * width:.1f},{pad + (1 - (v - mn) / (mx - mn)) * (height - 2 * pad):.1f}"
            for i, v in enumerate(values)
        )
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<polyline points="{pts}" fill="none" stroke="#3498db" stroke-width="1.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def _fmt(graph: dict, value, signed: bool = False):
    """
    Render a value using the graph's optional `format` (a Python format string,
    e.g. '${:,.0f}' or '{:.1f}%'). Non-numeric values and graphs without a
    format are returned unchanged. With signed=True a +/- prefix is added
    (the format is applied to the absolute value).
    """
    fmt = graph.get("format")
    if not fmt or not isinstance(value, (int, float)):
        return value
    text = fmt.format(abs(value) if signed else value)
    if signed:
        return ("+" if value > 0 else "-" if value < 0 else "") + text
    return text


def _rag(values: list[float], direction: str) -> str:
    """'good', 'bad', or '' comparing latest value to ~12 data points ago."""
    if not direction or len(values) < 2:
        return ""
    lookback = min(12, len(values) - 1)
    delta = values[-1] - values[-lookback - 1]
    if abs(delta) < 1e-9:
        return ""
    if direction == "lower_is_better":
        return "good" if delta < 0 else "bad"
    if direction == "higher_is_better":
        return "good" if delta > 0 else "bad"
    return ""


def _chart_series(graph: dict, cutoff: str) -> list[dict]:
    """[{x, y}] for Chart.js, limited to dates >= cutoff."""
    return [
        {"x": d, "y": v}
        for d, v in sorted(graph.get("data", {}).items())
        if d >= cutoff
    ]


def _overlay_all(overlay_ind: Indicator) -> list[dict]:
    """All overlay entries with no date filter — used for performance calculations."""
    if not overlay_ind.graphs:
        return []
    data = overlay_ind.graphs[0].get("data", {})
    return [
        {"date": d, "value": v["value"], "party": v["party"], "colour": v["colour"]}
        for d, v in sorted(data.items())
    ]


def _overlay_windowed(overlay_ind: Indicator, cutoff: str) -> list[dict]:
    """Overlay entries whose term overlaps with the chart window — used for chart display."""
    entries = _overlay_all(overlay_ind)
    result = []
    for i, e in enumerate(entries):
        next_d = entries[i + 1]["date"] if i + 1 < len(entries) else None
        if next_d is None or next_d > cutoff:
            result.append(e)
    return result


def _gov_performance(graph: dict, overlay: list[dict]) -> list[dict] | None:
    """
    For each government in overlay, calculate the delta (end - start) of the
    graph's metric during their term. Returns a list suitable for a bar chart,
    or None if direction is not set.
    """
    direction = graph.get("direction")
    if not direction or not overlay:
        return None

    data = sorted(
        [(d, v) for d, v in graph.get("data", {}).items() if isinstance(v, (int, float))]
    )
    if not data:
        return None

    result = []
    for i, gov in enumerate(overlay):
        next_gov = overlay[i + 1] if i + 1 < len(overlay) else None

        start_val = next((v for d, v in data if d >= gov["date"]), None)
        if next_gov:
            end_val = next((v for d, v in reversed(data) if d < next_gov["date"]), None)
        else:
            end_val = data[-1][1]

        if start_val is None or end_val is None:
            continue

        delta = end_val - start_val
        if abs(delta) < 1e-9:
            rag = "neutral"
        elif direction == "lower_is_better":
            rag = "good" if delta < 0 else "bad"
        else:
            rag = "good" if delta > 0 else "bad"

        # Surname only for compact bar labels
        surname = gov["value"].split()[-1]
        result.append({
            "label":     surname,
            "full_name": gov["value"],
            "party":     gov["party"],
            "colour":    gov["colour"],
            "delta":     round(delta, 4),
            "rag":       rag,
        })

    return result or None


def _kpi(graph: dict, overlay: list[dict]) -> dict | None:
    """
    Headline figure for the indicator page: latest value and date, plus its
    change since a baseline. The baseline is the first observation on or after
    the current government took office; with no government overlay (e.g. world
    indicators) it is the latest observation on or before 12 months earlier.
    RAG follows the graph's direction.
    """
    data = sorted(
        (d, v) for d, v in graph.get("data", {}).items() if isinstance(v, (int, float))
    )
    if not data:
        return None
    latest_date, latest = data[-1]
    direction = graph.get("direction", "")

    def rag_for(delta: float) -> str:
        if not direction or abs(delta) < 1e-9:
            return ""
        better = delta < 0 if direction == "lower_is_better" else delta > 0
        return "good" if better else "bad"

    kpi = {
        "value": _fmt(graph, latest), "date": latest_date, "label": graph.get("y", ""),
        "rag": "", "delta": None, "since_text": "",
    }

    if overlay:
        gov = overlay[-1]
        base = next(((d, v) for d, v in data if d >= gov["date"]), None)
        since_text = f"{gov['value']} took office ({gov['date']})"
    else:
        target = add_months(date.fromisoformat(latest_date), -12).isoformat()
        base = next(((d, v) for d, v in reversed(data) if d <= target), None)
        since_text = f"12 months ago ({base[0]})" if base else ""

    if base is not None:
        delta = round(latest - base[1], 4)
        kpi.update(
            delta=delta,
            delta_text=_fmt(graph, delta, signed=True) if graph.get("format") else f"{delta:+.2f}",
            rag=rag_for(delta),
            since_text=since_text,
        )
    return kpi


def _table_data(ind: Indicator) -> tuple[list[str], list[list]]:
    """
    (headers, rows) for the data table, most recent first.
    Each value cell is a dict {value, rag} where rag is 'good'/'bad'/'' based
    on the change from the previous period and the graph's direction.
    """
    cg = ind.chart_graphs
    if not cg:
        return [], []

    directions = [g.get("direction", "") for g in cg]
    all_dates = sorted(
        set().union(*(set(g.get("data", {}).keys()) for g in cg))
    )  # ascending for delta calc

    # Build rows ascending first so we can compute deltas
    asc_rows = []
    for d in all_dates:
        cells = []
        for g in cg:
            v = g.get("data", {}).get(d)
            cells.append(v)
        asc_rows.append((d, cells))

    # Now reverse for display and attach RAG based on delta vs previous row
    headers = ["Date"] + [g.get("y", f"Series {i + 1}") for i, g in enumerate(cg)]
    rows = []
    for row_i, (d, cells) in enumerate(reversed(asc_rows)):
        orig_i = len(asc_rows) - 1 - row_i
        display_cells = [d]
        for col_i, v in enumerate(cells):
            rag = ""
            if v is not None and orig_i > 0:
                prev_v = asc_rows[orig_i - 1][1][col_i]
                if prev_v is not None and isinstance(v, (int, float)) and isinstance(prev_v, (int, float)):
                    delta = v - prev_v
                    direction = directions[col_i]
                    if abs(delta) > 1e-9 and direction:
                        if direction == "lower_is_better":
                            rag = "good" if delta < 0 else "bad"
                        elif direction == "higher_is_better":
                            rag = "good" if delta > 0 else "bad"
            display_cells.append({"value": _fmt(cg[col_i], v) if v is not None else "", "rag": rag})
        rows.append(display_cells)

    return headers, rows


def _flags() -> dict[str, str]:
    """{jurisdiction name: flag path relative to the site root}, for flags that exist."""
    meta = yaml.safe_load(Path(JURISDICTIONS_FILE).read_text(encoding="utf-8")) or {}
    flags = {}
    for name, info in meta.items():
        path = f"static/flags/{info['iso']}.svg"
        if Path(path).exists():
            flags[name] = path
    return flags


def _last_run() -> str:
    """'YYYY-MM-DD HH:MM UTC' from lastrun.txt (written by the update workflow), or ''."""
    path = Path(LASTRUN_FILE)
    if not path.exists():
        return ""
    return datetime.fromisoformat(path.read_text().strip().replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")


# ── Jinja2 ────────────────────────────────────────────────────────────────────

def _env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        autoescape=jinja2.select_autoescape(["html"]),
    )
    env.globals["last_run"] = _last_run()
    env.filters["tojson"] = lambda v: json.dumps(v, default=str)
    return env


def _render(env: jinja2.Environment, template: str, path: str, **ctx) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    out = env.get_template(template).render(**ctx)
    Path(path).write_text(out, encoding="utf-8")
    print(f"  {path}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    env = _env()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cutoff = _cutoff()
    flags = _flags()
    world = load_events()
    if Path(STATIC_DIR).is_dir():
        shutil.copytree(STATIC_DIR, f"{OUTPUT_DIR}/{STATIC_DIR}", dirs_exist_ok=True)

    all_indicators: list[Indicator] = [
        Indicator(p) for p in sorted(Path("data").glob("*.yaml"))
    ]
    by_id: dict[str, Indicator] = {ind.id: ind for ind in all_indicators}

    chart_indicators = [ind for ind in all_indicators if not ind.is_overlay]

    by_jurisdiction: dict[str, list[Indicator]] = defaultdict(list)
    for ind in chart_indicators:
        by_jurisdiction[ind.jurisdiction].append(ind)

    # ── Home page ─────────────────────────────────────────────────────────────
    _render(env, "index.jinja", f"{OUTPUT_DIR}/index.html",
            jurisdictions=sorted(by_jurisdiction.keys()),
            flags=flags,
            page_id="index")

    # ── Status page ───────────────────────────────────────────────────────────
    status_rows = []
    for ind in sorted(all_indicators, key=lambda i: (i.jurisdiction, i.title)):
        graphs = ind.graphs
        latest = max(graphs[0].get("data", {}).items(), default=None) if graphs else None
        if latest is None:
            value = ""
        elif ind.is_overlay:
            value = latest[1]["value"]
        else:
            value = _fmt(graphs[0], latest[1])
        slug = ind.jurisdiction.lower().replace(" ", "_")
        status_rows.append({
            "jurisdiction": ind.jurisdiction,
            "title":        ind.title,
            "url":          None if ind.is_overlay else f"{slug}_{ind.id}.html",
            "value":        value,
            "last_updated": ind.last_updated,
            "freshness":    freshness(ind.last_updated, ind.frequency),
            "sourcing":     "Auto" if ind.collector else "Manual",
        })
    _render(env, "status.jinja", f"{OUTPUT_DIR}/status.html", rows=status_rows, page_id="status")

    # ── Per-jurisdiction pages ────────────────────────────────────────────────
    for jurisdiction, inds in sorted(by_jurisdiction.items()):
        slug = jurisdiction.lower().replace(" ", "_")

        by_cat: dict[str, list[dict]] = defaultdict(list)
        for ind in sorted(inds, key=lambda i: i.title):
            cg = ind.chart_graphs
            if not cg:
                continue
            direction = cg[0].get("direction", "")
            sorted_data = sorted(cg[0].get("data", {}).items())
            values = [v for _, v in sorted_data if isinstance(v, (int, float))]
            latest_date = sorted_data[-1][0] if sorted_data else None
            latest_val  = sorted_data[-1][1] if sorted_data else None

            overlay_id = cg[0].get("overlay_metric")
            kpi = _kpi(cg[0], _overlay_all(by_id[overlay_id]) if overlay_id in by_id else [])

            by_cat[ind.category].append({
                "id":           ind.id,
                "title":        ind.title,
                "url":          f"{slug}_{ind.id}.html",
                "sparkline":    _sparkline(values),
                "rag":          kpi["rag"] if kpi and kpi["delta"] is not None else _rag(values, direction),
                "delta":        kpi["delta"] if kpi else None,
                "delta_text":   kpi["delta_text"] if kpi and kpi["delta"] is not None else "",
                "latest_value": _fmt(cg[0], latest_val),
                "latest_date":  latest_date,
                "freshness":    freshness(ind.last_updated, ind.frequency),
                "y_label":      cg[0].get("y", ""),
            })

        _render(env, "jurisdiction.jinja", f"{OUTPUT_DIR}/{slug}.html",
                jurisdiction=jurisdiction,
                flag=flags.get(jurisdiction),
                slug=slug,
                categories=dict(sorted(by_cat.items())),
                page_id="jurisdiction")

        # ── Indicator detail pages ─────────────────────────────────────────────
        for ind in inds:
            cg = ind.chart_graphs
            if not cg:
                continue

            graphs: list[dict] = []
            overlays: dict[str, list[dict]] = {}

            for graph in cg:
                overlay_id = graph.get("overlay_metric")

                # Windowed overlay for chart display
                if overlay_id and overlay_id in by_id and overlay_id not in overlays:
                    overlays[overlay_id] = _overlay_windowed(by_id[overlay_id], cutoff)

                # Full overlay for government performance bars
                gov_perf = None
                if overlay_id and overlay_id in by_id and graph.get("direction"):
                    gov_perf = _gov_performance(graph, _overlay_all(by_id[overlay_id]))

                series = _chart_series(graph, cutoff)
                graphs.append({
                    "events":      events_for_range(world, series[0]["x"], series[-1]["x"]) if series else [],
                    "title":       graph.get("title", ""),
                    "y_label":     graph.get("y", ""),
                    "direction":   graph.get("direction", ""),
                    "overlay_id":  overlay_id,
                    "series":      series,
                    "gov_perf":    gov_perf,
                })

            first_overlay = cg[0].get("overlay_metric")
            kpi = _kpi(cg[0], _overlay_all(by_id[first_overlay])
                       if first_overlay in by_id else [])
            table_headers, table_rows = _table_data(ind)

            _render(env, "indicator.jinja",
                    f"{OUTPUT_DIR}/{slug}_{ind.id}.html",
                    jurisdiction=jurisdiction,
                    flag=flags.get(jurisdiction),
                    slug=slug,
                    ind=ind,
                    graphs=graphs,
                    kpi=kpi,
                    freshness=freshness(ind.last_updated, ind.frequency),
                    overlays=overlays,
                    table_headers=table_headers,
                    table_rows=table_rows,
                    page_id="indicator")


if __name__ == "__main__":
    main()
