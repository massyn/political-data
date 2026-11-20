# Update-data reference

Supporting detail for the update-data skill: source tables, collector reliability, SA/US notes, known limits and fix history. Moved out of CLAUDE.md.

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

| Indicator | Update Frequency | Typical Release Date | Manual Source |
|-----------|-----------------|---------------------|---------------|
| Unemployment Rate | Monthly | First Friday of month | [BLS series LNS14000000](https://data.bls.gov/timeseries/LNS14000000) |
| CPI (quarterly YoY) | Quarterly | Mid-month after quarter end | [BLS series CUSR0000SA0](https://data.bls.gov/timeseries/CUSR0000SA0) |
| Federal Funds Rate | Monthly | After FOMC meetings (8x/year) | [Federal Reserve H.15](https://www.federalreserve.gov/releases/h15/) |
| GDP Growth | Quarterly | Late Jan, Apr, Jul, Oct | [BEA National Accounts](https://www.bea.gov/data/gdp/gross-domestic-product) |
| Food Prices | Monthly | Mid-month | [BLS series CUSR0000SAF11](https://data.bls.gov/timeseries/CUSR0000SAF11) |
| Electricity Prices | Monthly | Mid-month | [BLS series APU000072610](https://data.bls.gov/timeseries/APU000072610) |
| Healthcare Costs | Monthly | Mid-month | [BLS series CUSR0000SEMD](https://data.bls.gov/timeseries/CUSR0000SEMD) |
| Rent Prices | Monthly | Mid-month | [BLS series CUSR0000SEHA](https://data.bls.gov/timeseries/CUSR0000SEHA) |
| Gasoline Prices | Monthly | Mid-month | [BLS series APU000074714](https://data.bls.gov/timeseries/APU000074714) |
| 30-Year Mortgage Rate | Monthly | Weekly, average by month | [Freddie Mac PMMS archive](https://www.freddiemac.com/pmms/archive) |
| Personal Savings Rate | Monthly | ~4 weeks after month end | [BEA PSAVERT](https://www.bea.gov/data/income-saving/personal-saving-rate) |
| Real Hourly Earnings | Quarterly | ~1 month after quarter end | [FRED LES1252881600Q](https://fred.stlouisfed.org/series/LES1252881600Q) (needs FRED_API_KEY) |
| Median Home Price | Quarterly | ~1 month after quarter end | [FRED MSPUS](https://fred.stlouisfed.org/series/MSPUS) (needs FRED_API_KEY) |
| President | Every 4 Years | Election day | [US National Archives](https://www.archives.gov/electoral-college) |

**Note:** BLS data pages (data.bls.gov) return JSON directly. FRED website pages return HTML but block direct programmatic access — use the FRED API with a key, or read the value manually from the page.


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


### Collector Reliability

| Collector | Method | Reliability | Notes |
|-----------|--------|-------------|-------|
| `us_unemployment.py` | BLS Public API | ✅ Reliable | Series LNS14000000 |
| `us_food_prices.py` | BLS Public API | ✅ Reliable | Series CUSR0000SAF11 |
| `us_electricity.py` | BLS Public API | ✅ Reliable | Series APU000072610 |
| `us_healthcare.py` | BLS Public API | ✅ Reliable | Series CUSR0000SEMD |
| `us_rent.py` | BLS Public API | ✅ Reliable | Series CUSR0000SEHA |
| `us_gasoline.py` | BLS Public API | ✅ Reliable | Series APU000074714 |
| `us_cpi.py` | BLS Public API | ✅ Reliable | Quarterly YoY from CUSR0000SA0 |
| `us_federal_funds.py` | Federal Reserve H.15 HTML | ⚠️ Fragile | Parse Fed HTML page |
| `us_mortgage.py` | Freddie Mac PMMS HTML | ⚠️ Fragile | Parse Freddie Mac archive |
| `us_gdp.py` | Trading Economics HTML | ⚠️ Fragile | Regex on GDP table |
| `us_personal_savings.py` | Trading Economics HTML | ⚠️ Fragile | Regex on page |
| `us_real_earnings.py` | FRED API | 🔑 Needs key | `FRED_API_KEY` required |
| `us_home_price.py` | FRED API | 🔑 Needs key | `FRED_API_KEY` required |
| `au_unemployment.py` | ABS Labour Force HTML | ⚠️ Fragile | Verified working 2026-09-03 (Jul 2026 → 4.5%). ABS wording changes break it. |
| `au_cash_rate.py` | RBA statistics HTML | ⚠️ Fragile | Rewritten 2026-09-03 — now reads the rate-*level* column (was reading the bp-*change* column and writing 0.0/0.25). RBA HTML works via plain `urllib` + unverified SSL even though WebFetch is 403'd. |
| `au_cpi.py` | ABS CPI HTML | ⚠️ Fragile | Rewritten 2026-09-03 — parses the monthly CPI movement table, emits quarter-end months only, YoY rate only (no index — see rebasing note). |
| `au_gdp.py` | ABS National Accounts HTML | ⚠️ Fragile | Verified working 2026-09-03 (Jun 2026 → 0.4%). ABS wording changes break it. |
| `au_wpi.py` | ABS WPI HTML | ⚠️ Fragile | Verified working 2026-09-03 (Jun 2026 → 3.2%). ABS wording changes break it. |
| `au_house_price.py` | ABS Total Value HTML | ⚠️ Fragile | Rewritten 2026-09-03 — matches the "mean price … to $X this quarter" sentence with a sanity bound (was grabbing the first `$` figure on the page, i.e. the total dwelling stock value in billions). |
| `sa_repo_rate.py` | Trading Economics HTML | ⚠️ Fragile | SARB site has TLS issues |
| `sa_cpi.py` | Trading Economics HTML | ⚠️ Fragile | Index is approximated from rate |
| `sa_unemployment.py` | Trading Economics HTML | ⚠️ Fragile | StatsSA PDFs not parseable |
| `sa_gdp.py` | Trading Economics HTML | ⚠️ Fragile | StatsSA PDFs not parseable |

**No collector (always manual):**
- `AU/prime_minister` — elections only
- `AU/emergency_department_wait_times` — annual AIHW publication
- `SA/president` — elections only
- `SA/murder_rate` — annual SAPS release, PDF-only
- `SA/residential_property_price_index` — StatsSA PDF, not machine-readable
- `US/president` — elections only

### API Keys

Two US collectors require a free FRED API key:

```bash
export FRED_API_KEY=your_key_here
```

Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html

Without the key, `us_real_earnings.py` and `us_home_price.py` will raise a `RuntimeError` and fall through to the manual list. The indicators these cover:
- `United States/real_hourly_earnings` — FRED series LES1252881600Q
- `United States/median_home_price` — FRED series MSPUS


### SA CPI Index Note

The SA CPI collector approximates the index using `prior_year_index × (1 + rate/100)` because StatsSA uses a different base period (Dec 2016=100) from what Trading Economics reports (2021=100). The approximation drifts slightly each year. If accuracy matters, manually verify against the StatsSA CPI publication.


### AI-Fetchable vs. Manual/Script-Only Sources

When checking freshness or pulling a new value for an AU indicator, use this to decide how:

| Source | AI-fetchable via WebFetch? | Notes |
|--------|---------------------------|-------|
| ABS release pages (`abs.gov.au/statistics/...`) | ✅ Yes | Renders fine via WebFetch. Use the specific quarter/month release URL (e.g. `.../mar-2026`), not just `/latest-release`, to get numbers rather than navigation links. |
| RBA (`rba.gov.au/...`) | ❌ No — returns HTTP 403 | `WebFetch` is blocked. Use `WebSearch` for the decision ("RBA cash rate <month> <year>"). Note `au_cash_rate.py` *can* reach `rba.gov.au` via plain `urllib` + `ssl._create_unverified_context()` — WebFetch's 403 is tool-specific. |
| AIHW (`aihw.gov.au/...`) | ✅ Yes | Works via WebFetch. |
| `collectors/au_cpi.py` (ABS CPI scraper) | ✅ Working (rewritten 2026-09-03) | Parses the monthly CPI movement table, emits the latest quarter-end month's YoY rate. Cross-check against the ABS release page. Does **not** emit the index value — the base-2011-12 index series is frozen pending a rebasing decision (see below). |
| `collectors/au_cash_rate.py` (RBA scraper) | ✅ Working (rewritten 2026-09-03) | Now reads the rate-level column (was reading the basis-point change → 0.0/0.25). Returns the last 24 board decisions. Cross-check the newest row against a news report of the RBA decision. |
| `collectors/au_gdp.py`, `au_wpi.py`, `au_unemployment.py` | ✅ Working (verified 2026-09-03) | ABS HTML scrapers, still fragile to wording changes. Cross-check the newest value against the specific ABS release page every run. |
| `collectors/au_house_price.py` (ABS Total Value scraper) | ✅ Working (rewritten 2026-09-03) | Matches the "mean price … to $X this quarter" sentence with a plausibility bound. The ABS release lags ~1 quarter (Jun-quarter figure lands ~late Sept). |

**Rule of thumb:** run `python update.py`, then for every indicator it flags (manual, error, or a value that fails a sanity check) go fetch the number yourself — ABS/AIHW via `WebFetch` on the specific release URL, RBA via `WebSearch`. Always eyeball the newest collector value against the source before trusting it: right ballpark, right period, right sign. If it doesn't match, don't append it — fix the collector, re-run, and update its status line in the two tables above with the date and the change. A collector writing one bad number into a live YAML is the failure mode that has bitten this project twice (`au_cash_rate.py`, `au_house_price.py`).

### 2026-07-27 Data Fixes

- **CPI**: added Mar 2026 quarter, YoY rate = 4.6% ([source](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/mar-2026)). The index-value series (base 2011-12=100) was **not** extended — ABS has rebased CPI reporting to Sep 2025=100 and no longer publishes on the old base, so continuing that series requires an explicit decision (rebase historical series, approximate via chaining, or stop the series) rather than a routine update. Ask before resuming it.
- **RBA cash rate**: removed ~15 corrupted rows (bogus 0.0/0.25 values at dates that didn't correspond to real decisions) left behind by a broken `au_cash_rate.py` run, and added the two real missing decisions: 2026-05-05 → 4.35% (third hike of the year), 2026-06-16 → 4.35% (hold).
- **ED wait times**: confirmed current (2024–25 FY, last_updated 2025-06-30 is still AIHW's latest published period) — no change needed.

### 2026-09-03 Data Fixes

- **CPI**: added Jun 2026 quarter, YoY rate = 3.8% ([source](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/jun-2026)). Index series still frozen (rebasing decision outstanding).
- **Median house price**: latest row was corrupted — `2026-03-31: 315000000.0` (the collector had grabbed the total dwelling-stock value change, $315.9bn). Corrected to the real Mar 2026 mean price, $1,111,100. No Jun 2026 quarter yet — ABS hadn't released it.
- **RBA cash rate**: `data/au_cash_rate.yaml` was corrupted *again* — 16 rows of 0.0/0.25 (basis-point changes, not rate levels) appended out of order by the broken collector, and the two real 2026 decisions sat at slightly wrong dates. Removed the garbage, realigned dates to the RBA's own table (`2026-05-06`, `2026-06-17`), and added the 12 Aug 2026 hold at 4.35%. The clean 2010–2026 level series is now correct.
- **Unemployment**: filled the Apr 2026 (4.5%) and May 2026 (4.4%) gap; Jun (4.4%) and Jul (4.5%) confirmed against ABS.
- **GDP / WPI**: Jun 2026 quarter values (0.4% / 3.2%) confirmed against ABS. WPI Mar 2026 quarter revised 3.3% → 3.2% to match the figure in the Jun 2026 release (original Mar 2026 release said 3.3%; ABS revises seasonally adjusted WPI annual rates by ~0.1pp between releases).
- **Collectors**: rewrote `au_cpi.py`, `au_cash_rate.py`, `au_house_price.py`; verified `au_gdp.py`, `au_wpi.py`, `au_unemployment.py` produce correct current values. All six now run as clean no-ops under `python update.py --force`.
- **`update.py` bug fix**: `Indicator.merge()` set `last_updated` from the newest *new* row, so a collector returning older backfill rows dragged `last_updated` backwards. It now uses the newest date across all data.

### Known Technical Limitations

These have been hit before — don't repeat the same mistakes:

| Issue | Detail |
|-------|--------|
| **FRED blocks direct HTTP** | `fred.stlouisfed.org` returns 403 to programmatic requests. Do not attempt to scrape FRED HTML pages. Use the BLS Public API (no auth) for BLS series, or the FRED REST API with `FRED_API_KEY` for FRED-only series. |
| **SARB website TLS error** | `resbank.co.za` has a certificate alt-name mismatch. Cannot be fetched programmatically. Use Trading Economics as the SA repo rate source instead. |
| **StatsSA PDFs** | StatsSA publishes most detailed data as PDFs. These return binary content and cannot be parsed. SA RPPI, murder rate detail, and historical CPI are manual-only for this reason. |
| **ABS pages require JS** | ABS pages may return empty or incomplete HTML via plain `urllib.request`. The WebFetch tool (headless browser) works; plain Python HTTP may not. AU collectors are marked fragile for this reason. |
| **Trading Economics rate-limiting** | HTML scraping Trading Economics works but can be blocked without a browser-like User-Agent. If a SA or US GDP/savings collector fails with HTTP 403 or 429, the value must be entered manually. |
| **BLS API returns last 3 years only** | The BLS Public API v1 (no auth) returns only 3 years of data per request. This is fine for updates but insufficient for historical backfills — for those, download the full series CSV from the BLS website manually. |
| **Freddie Mac PMMS date format** | The PMMS archive uses US date format (MM/DD/YYYY). The `us_mortgage.py` collector handles this, but if the page structure changes the regex will break. |

