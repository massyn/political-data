# Political Data - Data Schema Documentation

This project tracks political accountability through objective, measurable indicators across jurisdictions.

## CRITICAL: Data Currency Requirements

**Data must be kept current at all times. Out-of-date data destroys credibility.**

### Mandatory Update Frequency

All indicators MUST be updated according to their frequency:
- **Monthly indicators**: Updated within 2 weeks of official data release (e.g., Unemployment Rate)
- **Quarterly indicators**: Updated within 3 weeks of official data release (e.g., CPI, GDP Growth, Wage Price Index, Median House Price)
- **Annual indicators**: Updated within 1 month of official data release (e.g., ED Wait Times)
- **Election data**: Updated within 24 hours of official election results

### Maximum Data Staleness

**UNACCEPTABLE:**
- Monthly data more than 1 month old
- Quarterly data more than 1 quarter old
- Annual data more than 1 year old
- Missing the most recent government term

### Data Currency Validation

Before committing ANY changes:
1. Check the latest data point for EVERY indicator
2. Compare against current date
3. Update ALL stale indicators before committing
4. Validate using `python build.py`

**A dashboard with stale data is worse than no dashboard at all.**

## Data Structure

Current layout — one flat file per indicator, observations inline, **no `data.csv`**:

```
/data
  au_consumer_price_index.yaml
  au_cash_rate.yaml
  ...
```

Each file carries `id`, `jurisdiction`, `title`, `category`, `frequency`, `source`,
`last_updated`, `description`, and a `graph` block; every chart entry in `graph`
holds its observations inline as a `data:` map of `YYYY-MM-DD: value`.

## Indicator Schema

Every indicator must include the following fields:

### Required Fields

- **title** (string): Human-readable name of the indicator
- **category** (string): Must be one of:
  - `Government`
  - `Cost of Living`
  - `Housing`
  - `Safety & Crime`
  - `Health`
  - `Education`
  - `Employment`
  - `Economy`
- **frequency** (string): How often data is collected. Must be one of:
  - `Month`
  - `Quarter`
  - `Annual`
  - `3 Year`
- **source** (string): URL or reference to the authoritative data source
- **last_updated** (string): ISO date of the most recent data point in the file. Update this every time new data is appended. This is the primary freshness signal — compare against today's date and frequency to determine if the indicator is stale.
- **collector** (string, optional): Path to the Python collector script relative to the project root (e.g. `collectors/us_unemployment.py`). If present, `python update.py` will run this script to fetch new data automatically. If absent, the indicator is manually maintained. The script must export a `collect()` function returning `list[tuple]`.
- **description** (string): Detailed explanation of what the indicator measures, including any special fields or values
- **graph** (boolean or list): Controls visualization of the indicator
  - Set to `False` to display only a data table
  - Set to a list of graph configurations to render Chart.js visualizations
  - Each graph configuration must include:
    - `x`: The field name to use for the x-axis (typically `date`)
    - `y`: The field name to use for the y-axis (the value to plot)
    - `title`: The title for the graph
    - `overlay_metric` (optional): The ID of another indicator to overlay on the graph
      - Used to show contextual information like government changes
      - Draws vertical lines at each date in the overlay metric
      - Colors the background between dates using the `colour` field from the overlay metric
      - Typically used to overlay `prime_minister` on economic indicators
    - `direction` (optional): Indicates whether higher or lower values are better for RAG scoring
      - Set to `higher_is_better` for metrics where increases are positive (e.g., GDP growth, wage growth, ED performance)
      - Set to `lower_is_better` for metrics where decreases are positive (e.g., unemployment, inflation, house prices)
      - Used to calculate government performance scorecards with Red-Amber-Green (RAG) status

### Examples

For the live format read `data/au_consumer_price_index.yaml` (charts, `overlay_metric`) and `data/au_prime_minister.yaml` (table only, `graph: False`).

## Validation Requirements

**IMPORTANT: All indicators must pass validation before being committed.**

Validation runs as part of the build:
```bash
python build.py
```

### Validation Checks

Each indicator is a single flat file, `data/<id>.yaml` (there are no per-indicator
folders and no `data.csv`). `build.py` loads every one through `update.Indicator`
and will raise if a file is missing `id`, `jurisdiction`, `title`, `frequency`, or
`last_updated`, or if its `graph` block is malformed. `update.py` uses the same
loader, so `python update.py --dry-run` is also a quick structural check.

`category` must be one of the allowed values and `frequency` one of `Month`,
`Quarter`, `Annual`, `3 Year`.

### Success Criteria

`python build.py` exits 0 and prints the list of rendered `./dist/*.html` pages
(one `index`, one per jurisdiction, one per indicator). A traceback means a YAML
file is malformed — fix it before committing.

## Adding a New Indicator

1. Create `data/<id>.yaml` (e.g. `data/au_new_indicator.yaml`) with `id`,
   `jurisdiction`, `title`, `category`, `frequency`, `source`, `last_updated`,
   `description`, and a `graph` block. Copy an existing AU file as a template.
2. Put the observations inline under `graph[].data` as `YYYY-MM-DD: value`.
3. Add a `collector:` line only if you also write `collectors/<id>.py` exporting
   `collect() -> list[tuple]`.
4. Run `python build.py` to validate and render.
5. Fix any errors; commit only when it builds clean.

## Updating Existing Indicators

**This is the most common operation.** Data must be kept current according to the frequency requirements.

### Checking Freshness

Use `last_updated` in `data/<id>.yaml` as the primary freshness signal. Compare it against today's date and the indicator's `frequency` to determine if data is stale:
- `Month` frequency → stale if `last_updated` is more than ~6 weeks ago
- `Quarter` frequency → stale if `last_updated` is more than ~4 months ago
- `Annual` frequency → stale if `last_updated` is more than ~13 months ago

### Updating

Use the \`update-data\` project skill (\`.claude/skills/update-data/SKILL.md\`): run \`python update.py\`, verify every new value against its official source, hand-fill what the collectors missed, then validate with \`python build.py\`.

### Handling Data Revisions

Sometimes official sources revise historical data:

1. **Check for revision notes** in the source publication
2. **Update historical values** if revisions are significant
3. **Document the revision** in the commit message
4. **Note methodology changes** in indicator description if applicable

## Automated Data Collection

The project uses a collector system to automate data updates. Run everything via:

```bash
python update.py              # update all stale indicators
python update.py --dry-run    # show what would change, no writes
python update.py --force      # update everything regardless of staleness
python update.py unemployment # target a specific indicator by name substring
```

`update.py` scans every `data/<id>.yaml`, checks staleness against `last_updated` and `frequency`, runs the `collector:` script if present, appends new rows to the indicator YAML, and updates `last_updated`. Run `python build.py` afterwards to validate and render.

### The `collector:` Field

Each `data/<id>.yaml` may include a `collector:` field pointing to its collector script:

```yaml
collector: collectors/us_unemployment.py
```

If the field is absent, the indicator is permanently manual. The collector script must export a `collect()` function that returns a list of tuples — one tuple per data row — in `(date, value[, ...])` order, where `date` is `YYYY-MM-DD`. You can run any collector directly to test it:

```bash
python collectors/us_unemployment.py   # prints latest rows as tab-separated values
```

## Best Practices

### Data Sources
- Use official government statistics when available (e.g., ABS, AEC, RBA)
- Always cite authoritative sources in the `source` field
- Prefer data that cannot be revised or manipulated

### Dates
- Use consistent date formats (ISO 8601: YYYY-MM-DD)
- Record the END of the measurement period
- For elections, use the election date (not swearing-in date)
- For quarterly data, use the last day of the quarter (Mar 31, Jun 30, Sep 30, Dec 31)

### Data Quality
- Ensure data is complete and accurate
- Verify calculations (e.g., inflation rates)
- Include all historical data available
- Don't skip periods unless data doesn't exist

### Descriptions
- Clearly explain what the indicator measures
- Define any specialized fields or values
- Explain the difference between multiple value fields (e.g., rate vs. index)
- Include context about base periods or reference points

## Project Philosophy

This project exists to make political accountability impossible to spin. Every metric must be:
- **Independently collected** (not by the government being evaluated)
- **Publicly verifiable** (raw data, sources published)
- **Historically preserved** (version controlled, cannot be deleted)
- **Simply presented** (clear, understandable metrics)

When adding indicators, ask:
- Can this be objectively measured?
- Can citizens verify this data?
- Will this help hold governments accountable?
