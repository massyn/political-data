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
4. Validate using `python data.py`

**A dashboard with stale data is worse than no dashboard at all.**

## Data Structure

```
/data
  /{jurisdiction}
    /{indicator_name}
      indicator.yaml
      data.csv
```

## Indicator Schema (indicator.yaml)

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
- **last_updated** (string): ISO date of the most recent data point in data.csv. Update this every time new data is appended. This is the primary freshness signal — compare against today's date and frequency to determine if the indicator is stale.
- **description** (string): Detailed explanation of what the indicator measures, including any special fields or values
- **schema** (dictionary): Defines the CSV columns and their meaning
  - Must include `date` field
  - Additional fields as needed for the indicator
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

### Example: Consumer Price Index (with graphs)

```yaml
title: Consumer Price Index (CPI)
category: Cost of Living
frequency: Quarter
source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia
last_updated: 2025-12-31
description: This indicator tracks the Consumer Price Index (CPI) for Australia, measuring changes in the cost of living over time. The 'value' field represents the year-over-year inflation rate as a percentage (e.g., 3.24% means prices rose 3.24% compared to the same quarter last year). The 'index' field is the absolute CPI index value using 2011-12 as the base period (100), allowing for long-term price comparisons.
schema:
  date: The date of the CPI measurement (end of quarter)
  value: The year-over-year inflation rate (percentage change)
  index: The CPI index value (base period 2011-12 = 100)
graph:
  - x: date
    y: value
    title: Percentage change
    overlay_metric: prime_minister
  - x: date
    y: index
    title: CPI Index value
    overlay_metric: prime_minister
```

### Example: Prime Minister (table only)

```yaml
title: Prime Minister of Australia
category: Government
frequency: 3 Year
source: https://results.aec.gov.au/
description: This indicator tracks who the Prime Minister of Australia is following each federal election. It is recorded at every election, even when the incumbent wins re-election, allowing tracking of government continuity and change over time.
schema:
  date: The date the prime minister won the last election
  value: The full name of the Prime Minister
  party: The name of the party
  colour: The RGB colour used to indicate the party
graph: False
```

## Data File (data.csv)

- Must be valid CSV format
- First row must contain column headers matching the schema fields
- `date` column must be in ISO format: `YYYY-MM-DD`
- All dates should represent the END of the measurement period (e.g., end of quarter, end of year)
- Data should be in chronological order
- Missing values should be left blank (not "N/A" or "null")

### Example: CPI Data

```csv
date,value,index
2020-03-31,2.19,116.6
2020-06-30,-0.35,114.4
2020-09-30,0.69,116.2
```

### Example: Prime Minister Data

```csv
date,name,party,colour
1901-03-29,Edmund Barton,Protectionist,#8B4513
1903-12-16,Alfred Deakin,Protectionist,#8B4513
1906-12-12,Alfred Deakin,Protectionist,#8B4513
```

## Validation Requirements

**IMPORTANT: All indicators must pass validation before being committed.**

Run the validation script:
```bash
python data.py
```

### Validation Checks

The `data.py` script validates:
- All required fields are present in `indicator.yaml`
- Category values are from the allowed list
- Frequency values are from the allowed list
- Schema is a dictionary
- All indicators have corresponding CSV files

### Success Criteria

A successful validation shows:
```
INFO   Jurisdiction ==> Australia
INFO      Indicator ==> consumer_price_index
INFO      Indicator ==> prime_minister
```

**No ERROR messages should appear.**

If you see ERROR messages, they must be fixed before the data is considered valid.

## Adding a New Indicator

1. Create a new folder: `data/{jurisdiction}/{indicator_name}/`
2. Create `indicator.yaml` with all required fields
3. Create `data.csv` with appropriate columns matching the schema
4. Run `python data.py` to validate
5. Fix any validation errors
6. Commit only when validation passes

## Updating Existing Indicators

**This is the most common operation.** Data must be kept current according to the frequency requirements.

### Checking Freshness

Use `last_updated` in `indicator.yaml` as the primary freshness signal. Compare it against today's date and the indicator's `frequency` to determine if data is stale:
- `Month` frequency → stale if `last_updated` is more than ~6 weeks ago
- `Quarter` frequency → stale if `last_updated` is more than ~4 months ago
- `Annual` frequency → stale if `last_updated` is more than ~13 months ago

### Update Workflow

1. **Identify stale indicators** — scan `last_updated` in each `indicator.yaml` and compare to today's date and frequency.

2. **Look up the latest data** — visit the `source` URL in `indicator.yaml` and find the most recently published figure. Do not build scripts; just fetch the page and read the value.

3. **Append new rows to `data.csv`** — add one row per new period, in chronological order, using `YYYY-MM-DD` end-of-period dates.

4. **Update `last_updated` in `indicator.yaml`** — set it to the date of the most recent data point just added.

5. **Validate** — run `python data.py` to confirm no schema errors.

6. **Commit** — include the data period in the message, e.g. `"Update US unemployment through Jan 2026"`.

### Data Sources Quick Reference

#### Australia

| Indicator | Update Frequency | Typical Release Date | Source |
|-----------|-----------------|---------------------|---------|
| Unemployment Rate | Monthly | Mid-month for previous month | [ABS Labour Force](https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release) |
| CPI | Quarterly | Late Jan, Apr, Jul, Oct | [ABS CPI](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release) |
| GDP Growth | Quarterly | Early Mar, Jun, Sep, Dec | [ABS National Accounts](https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release) |
| Wage Price Index | Quarterly | Mid-Feb, May, Aug, Nov | [ABS WPI](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release) |
| Median House Price | Quarterly | Variable | [ABS Total Value of Dwellings](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release) |
| RBA Cash Rate | Monthly | First Tue of month | [RBA](https://www.rba.gov.au/statistics/cash-rate/) |
| ED Wait Times | Annual | Variable | [AIHW](https://www.aihw.gov.au/hospitals/topics/emergency-departments/time-spent-in-emergency) |

#### South Africa

| Indicator | Update Frequency | Typical Release Date | Source |
|-----------|-----------------|---------------------|---------|
| Unemployment Rate | Quarterly | Mid-Feb, May, Aug, Nov | [StatsSA QLFS](https://www.statssa.gov.za/) |
| CPI | Quarterly | Late Jan, Apr, Jul, Oct | [StatsSA CPI](https://www.statssa.gov.za/?page_id=1871) |
| GDP Growth | Quarterly | Early Mar, Jun, Sep, Dec | [StatsSA GDP](https://www.statssa.gov.za/) |
| SARB Repo Rate | Monthly | Third Thu of Jan, Mar, May, Jul, Sep, Nov | [SARB Rates](https://www.resbank.co.za/Research/Rates/Pages/Rates-Home.aspx) |
| Residential Property Price Index | Quarterly | Variable (2-3 months after quarter end) | [StatsSA RPPI](https://www.statssa.gov.za/?p=17490) |
| Murder Rate | Annual | August/September (for Apr-Mar period) | [SAPS Crime Stats](https://www.saps.gov.za/) |

#### United States

| Indicator | Update Frequency | Typical Release Date | Source |
|-----------|-----------------|---------------------|---------|
| Unemployment Rate | Monthly | First Friday of month (for previous month) | [BLS/FRED: UNRATE](https://fred.stlouisfed.org/series/UNRATE) |
| CPI | Monthly | Mid-month (for previous month) | [BLS/FRED: CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL) |
| Federal Funds Rate | Monthly | Daily updates, FOMC decisions 8x per year | [Federal Reserve/FRED: FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS) |
| GDP Growth | Quarterly | Late Jan, Apr, Jul, Oct (one month after quarter end) | [BEA/FRED: GDPC1](https://fred.stlouisfed.org/series/GDPC1) |
| President | Every 4 Years | First Tuesday after first Monday in November | [US National Archives](https://www.archives.gov/electoral-college) |

**Note:** US data is available directly from the source URLs listed in each `indicator.yaml`. For FRED series, the data page (e.g. `https://fred.stlouisfed.org/series/UNRATE`) shows the latest value and allows downloading the full series as CSV. Simply look up the value and append it to `data.csv`.

### Monthly Update Checklist

Run this checklist at the start of each month:

#### Australia
- [ ] Check ABS release calendar for new data
- [ ] Update Unemployment Rate (released mid-month)
- [ ] Update RBA Cash Rate (if changed, first Tuesday)
- [ ] Check for quarterly releases:
  - [ ] CPI (Jan, Apr, Jul, Oct)
  - [ ] GDP (Mar, Jun, Sep, Dec)
  - [ ] WPI (Feb, May, Aug, Nov)
  - [ ] House Prices (quarterly, variable release)

#### South Africa
- [ ] Check StatsSA release calendar for new data
- [ ] Update SARB Repo Rate (if changed, third Thursday of Jan, Mar, May, Jul, Sep, Nov)
- [ ] Check for quarterly releases:
  - [ ] Unemployment Rate (Feb, May, Aug, Nov)
  - [ ] CPI (Jan, Apr, Jul, Oct)
  - [ ] GDP Growth (Mar, Jun, Sep, Dec)
  - [ ] Residential Property Price Index (2-3 months after quarter end)
- [ ] Check for annual releases:
  - [ ] Murder Rate (Aug/Sep for Apr-Mar period)

#### United States
- [ ] Check FRED for new data releases
- [ ] Update Unemployment Rate (released first Friday of month)
- [ ] Update CPI (released mid-month)
- [ ] Update Federal Funds Rate (updates daily on FRED, check after FOMC meetings)
- [ ] Check for quarterly releases:
  - [ ] GDP Growth (late Jan, Apr, Jul, Oct)
  - [ ] Median Home Price (variable)
  - [ ] Real Hourly Earnings (quarterly)

#### Validation & Deployment
- [ ] Run `python data.py` to validate
- [ ] Run `python build.py` to test
- [ ] Commit and push updates

### South Africa Data Collection Notes

**Key Data Agencies:**
- **Statistics South Africa (StatsSA)**: Official national statistics organization - primary source for economic and social data
- **South African Reserve Bank (SARB)**: Central bank - source for monetary policy and financial data
- **South African Police Service (SAPS)**: Source for crime statistics

**Important Considerations:**
1. **Historical Data Limitations**: Some official data only goes back to 1994 (post-apartheid transition). Earlier data may exist from other sources but should be validated carefully.
2. **Quarterly Data Timing**: South Africa uses calendar quarters (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
3. **Annual Crime Data**: SAPS crime statistics follow the fiscal year (April 1 to March 31) and are typically released 4-5 months after the period ends
4. **SARB Meeting Schedule**: The Monetary Policy Committee (MPC) meets 6 times per year, typically on the third Thursday of Jan, Mar, May, Jul, Sep, and Nov
5. **StatsSA Release Calendar**: Check the StatsSA release calendar regularly for exact publication dates: https://www.statssa.gov.za/?page_id=1847

**Data Quality:**
- StatsSA data is generally reliable and meets international standards (SDDS compliant)
- Historical revisions are common for GDP and other economic indicators
- Crime statistics methodology has remained consistent since 1994

**Historical Backfill Priority:**
For comprehensive analysis, prioritize backfilling data to at least 2000 (start of democratic consolidation):
1. President (complete from 1975)
2. CPI - available from StatsSA historical archives
3. Unemployment Rate - QLFS data from 2008, earlier surveys available
4. GDP Growth - available from 1960s
5. SARB Repo Rate - available from 1998
6. Property Prices - FRED has data from 1966
7. Murder Rate - SAPS data from 1994

### Handling Data Revisions

Sometimes official sources revise historical data:

1. **Check for revision notes** in the source publication
2. **Update historical values** if revisions are significant
3. **Document the revision** in the commit message
4. **Note methodology changes** in indicator.yaml description if applicable

### Data Currency Check

Before any commit, verify data currency by scanning `last_updated` in each `indicator.yaml`. Compare each value to today's date and the indicator's `frequency`. Any indicator where `last_updated` is beyond the staleness threshold must be updated before committing.

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
