"""
build.py — static site generator for the data indicator schema.

Usage:
    python build.py           # builds to ./dist
    python build.py ./out     # builds to ./out
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import jinja2

from update import Indicator

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "./dist"
TEMPLATE_DIR = "templates"
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
            display_cells.append({"value": v if v is not None else "", "rag": rag})
        rows.append(display_cells)

    return headers, rows


# ── Jinja2 ────────────────────────────────────────────────────────────────────

def _env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        autoescape=jinja2.select_autoescape(["html"]),
    )
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
            page_id="index")

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

            by_cat[ind.category].append({
                "id":           ind.id,
                "title":        ind.title,
                "url":          f"{slug}_{ind.id}.html",
                "sparkline":    _sparkline(values),
                "rag":          _rag(values, direction),
                "latest_value": latest_val,
                "latest_date":  latest_date,
                "y_label":      cg[0].get("y", ""),
            })

        _render(env, "jurisdiction.jinja", f"{OUTPUT_DIR}/{slug}.html",
                jurisdiction=jurisdiction,
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

                graphs.append({
                    "title":       graph.get("title", ""),
                    "y_label":     graph.get("y", ""),
                    "direction":   graph.get("direction", ""),
                    "overlay_id":  overlay_id,
                    "series":      _chart_series(graph, cutoff),
                    "gov_perf":    gov_perf,
                })

            table_headers, table_rows = _table_data(ind)

            _render(env, "indicator.jinja",
                    f"{OUTPUT_DIR}/{slug}_{ind.id}.html",
                    jurisdiction=jurisdiction,
                    slug=slug,
                    ind=ind,
                    graphs=graphs,
                    overlays=overlays,
                    table_headers=table_headers,
                    table_rows=table_rows,
                    page_id="indicator")


if __name__ == "__main__":
    main()
