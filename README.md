# political-data

Political accountability through objective, measurable indicators.

→ [https://political-data.pages.dev/](https://political-data.pages.dev/)

---

## Data Schema (v2)

All v2 indicators live as single YAML files under `datav2/`. Metadata and data are
co-located in one file per indicator — no separate CSV files.

### Directory layout

```
datav2/
  au_prime_minister.yaml
  au_consumer_price_index.yaml
  us_unemployment_rate.yaml
  ...
```

### Naming convention

File names are the indicator `id` — a lowercase, underscore-separated slug prefixed
with a two-letter jurisdiction code:

| Prefix | Jurisdiction |
|--------|-------------|
| `au_`  | Australia |
| `sa_`  | South Africa |
| `us_`  | United States |

---

### Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique slug (e.g. `au_prime_minister`). Used in `overlay_metric` cross-references. |
| `jurisdiction` | Yes | Country or region name (e.g. `Australia`) |
| `title` | Yes | Human-readable indicator name |
| `category` | Yes | One of: `Government`, `Cost of Living`, `Housing`, `Safety & Crime`, `Health`, `Education`, `Employment`, `Economy` |
| `frequency` | Yes | One of: `Month`, `Quarter`, `Annual`, `3 Year` |
| `source` | Yes | URL to the authoritative data source |
| `last_updated` | Yes | ISO date (`YYYY-MM-DD`) of the most recent data point. Updated automatically on each successful collection run. |
| `collector` | No | Relative path to a collector script (e.g. `collectors/au_cpi.py`). Omit for manually-maintained indicators. |
| `description` | Yes | Plain-text explanation of what the indicator measures |
| `graph` | Yes | List of one or more graph entries (see below) |

---

### Graph entries

Every indicator's data lives inside its `graph` entries. Each entry is self-contained:
it describes how to visualise one series and carries the data for that series. Adding a
new measurement series is just adding another entry to the list.

There are two entry shapes: **charted series** and **overlay records**.

---

#### Charted series

Rendered as a line chart. Requires `x` and `y` axis descriptors plus a `data` dict
keyed by ISO date.

```yaml
graph:
  - x: date
    y: Unemployment rate (%)         # axis label — also the series description
    title: Unemployment Rate         # chart heading
    overlay_metric: au_prime_minister   # optional: id of an overlay record
    direction: lower_is_better          # optional: lower_is_better | higher_is_better
    data:
      2010-01-31: 5.3
      2010-02-28: 5.3
      2010-03-31: 5.4
```

An indicator with two independent series (e.g. rate + index) has two entries, each
with its own `data` dict:

```yaml
graph:
  - x: date
    y: Year-over-year inflation rate (%)
    title: Percentage Change
    overlay_metric: au_prime_minister
    direction: lower_is_better
    data:
      2010-03-31: 2.93
      2010-06-30: 3.13
  - x: date
    y: CPI index value (base 2011-12 = 100)
    title: CPI Index Value
    overlay_metric: au_prime_minister
    data:
      2010-03-31: 95.2
      2010-06-30: 95.8
```

---

#### Overlay / government records

A reference dataset used to colour chart backgrounds by government period. Not rendered
as a standalone chart. Has no `x`/`y` fields. Data values are dicts with `value`,
`party`, and `colour`.

```yaml
graph:
  - title: Prime Minister of Australia
    data:
      2019-05-18:
        value: Scott Morrison
        party: Liberal
        colour: "#0047AB"
      2022-05-21:
        value: Anthony Albanese
        party: Labor
        colour: "#E13940"
```

The renderer identifies overlay records by the absence of `x`/`y` fields and the
presence of `colour` in data values.

---

### Data key format

All `data:` keys are ISO dates (`YYYY-MM-DD`) representing the **end of the measurement
period**:

- End of month → `2026-01-31`
- End of quarter → `2026-03-31`
- Election / event date → `2022-05-21`

---

### Collector scripts

If `collector:` is set, `updatev2.py` dynamically loads that module and calls
`collect()`. The function must return `list[tuple]` where:

- `row[0]` is an ISO date string
- `row[1]` maps to the **first** charted graph entry's data
- `row[2]` (if present) maps to the **second** charted graph entry's data
- and so on, in graph entry order

```python
def collect() -> list[tuple]:
    # example: CPI returns (date, inflation_rate, index_value)
    return [("2026-03-31", 2.4, 141.2)]
```

Overlay / government records have no collector — they are always manually maintained.

---

### Staleness thresholds

`updatev2.py` flags an indicator as stale when `last_updated` is older than:

| Frequency | Threshold |
|-----------|-----------|
| `Month`   | 42 days   |
| `Quarter` | 120 days  |
| `Annual`  | 400 days  |
| `3 Year`  | 1 280 days |

---

### Running updates

```bash
python updatev2.py                 # update all stale indicators
python updatev2.py --dry-run       # preview changes, no writes
python updatev2.py --force         # update all regardless of staleness
python updatev2.py cpi             # target a specific indicator by id substring
```

---

### Adding a new indicator

1. Create `datav2/{id}.yaml` with all required top-level fields.
2. Add one graph entry per series.
   - Charted: include `x`, `y`, `direction` (if applicable), and `data`.
   - Overlay: include `title` and `data` with `value`/`party`/`colour` per date.
3. If automated, add a `collector:` path to a script exporting
   `collect() -> list[tuple]`. Column order after `date` must match graph entry order.
4. Run `python updatev2.py {id}` to verify it loads and reports the correct status.
