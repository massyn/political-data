# Australian Economic Data Collection Summary

## Status Report

### Successfully Collected

#### 1. Consumer Price Index (CPI) - COMPLETE
**File**: `CPI_DATA_2010_2025.csv`

**Data Coverage**: March 2010 - September 2025 (63 quarters)

**Columns**:
- `date`: End of quarter in YYYY-MM-DD format
- `value`: Year-over-year inflation rate (percentage)
- `index`: CPI index value (base period 2011-12 = 100)

**Source**: Australian Bureau of Statistics via rateinflation.com

**Status**: ✓ Complete quarterly data from Q1 2010 to Q3 2025

**Notes**:
- All quarterly data points collected
- Inflation rates calculated as year-over-year percentage changes
- Index values directly from ABS data
- Data is current as of September 2025

---

### Partially Collected (Samples Only)

#### 2. Unemployment Rate - SAMPLE ONLY (2024-2025)
**File**: `UNEMPLOYMENT_DATA_SAMPLE_2024_2025.csv`

**Data Coverage**: January 2024 - October 2025 (22 months)

**Columns**:
- `date`: End of month in YYYY-MM-DD format
- `value`: Seasonally adjusted unemployment rate (percentage)

**Source**: Australian Bureau of Statistics Labour Force Australia releases

**Status**: ⚠️ INCOMPLETE - Sample data only from 2024-2025

**Required Action**:
- Download historical monthly data from 2010-2023
- Access ABS Labour Force Australia publication (Catalogue 6202.0)
- Extract seasonally adjusted unemployment rate column
- Complete the time series back to January 2010

**Download Instructions**:
1. Visit: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release
2. Navigate to "Data downloads" section
3. Download time series Excel spreadsheet
4. Extract Table 1: Labour Force Status - Seasonally Adjusted
5. Use unemployment rate column for all months from January 2010

---

#### 3. GDP Growth - SAMPLE ONLY (2024-2025)
**File**: `GDP_GROWTH_DATA_SAMPLE_2024_2025.csv`

**Data Coverage**: March 2024 - June 2025 (6 quarters)

**Columns**:
- `date`: End of quarter in YYYY-MM-DD format
- `value`: Quarter-on-quarter GDP growth rate (percentage, seasonally adjusted)

**Source**: Australian Bureau of Statistics National Accounts

**Status**: ⚠️ INCOMPLETE - Sample data only from 2024-2025

**Required Action**:
- Download historical quarterly data from 2010-2023
- Access ABS Australian National Accounts publication
- Extract seasonally adjusted GDP chain volume measures
- Complete the time series back to March 2010

**Download Instructions**:
1. Visit: https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release
2. Navigate to "Data downloads" section
3. Download time series Excel spreadsheet
4. Extract Table 1: Key Aggregates - Seasonally Adjusted
5. Use GDP chain volume measures percentage change column
6. Collect all quarters from March 2010

---

### Not Yet Collected

#### 4. Wage Price Index - NOT COLLECTED
**Status**: ❌ NO DATA COLLECTED

**Required Data**:
- Date (end of quarter)
- Annual wage growth (year-over-year percentage change)
- Wage Price Index value (base period 2008-09 = 100)

**Source**: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia

**Required Action**:
1. Visit the Wage Price Index Australia latest release page
2. Download time series Excel spreadsheet
3. Extract Total Hourly Rates of Pay Excluding Bonuses - All Sectors
4. Collect both index values and annual percentage changes
5. Data needed from March 2010 to most recent quarter

**Note**: WPI data has been published quarterly since September 1997, so full historical data should be available.

---

#### 5. Median House Price - NOT COLLECTED
**Status**: ❌ NO DATA COLLECTED - REQUIRES ALTERNATIVE SOURCE

**Challenge**: The ABS "Residential Property Price Indexes: Eight Capital Cities" publication was DISCONTINUED in December 2021.

**Required Data**:
- Date (end of quarter)
- Median dwelling price for all capital cities combined (AUD)

**Alternative Data Sources**:

**Option 1: ABS Total Value of Dwellings (2022-Present)**
- URL: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release
- Coverage: June 2022 onwards
- Includes mean and median prices by city
- Would need to calculate weighted average for all capitals

**Option 2: Historical RPPI Data (2010-2021)**
- Access archived ABS Residential Property Price Indexes releases
- Coverage: September 2003 - December 2021
- Need to extract capital city combined index/median

**Option 3: FRED Database (Complete Series)**
- URL: https://fred.stlouisfed.org/series/QAUR628BIS
- Real Residential Property Prices for Australia
- Coverage: Q1 1970 - Q2 2025
- Downloadable CSV format
- Based on BIS data, may differ from ABS methodology

**Recommended Approach**:
1. Use FRED data for consistent series 2010-2025 (easiest), OR
2. Combine historical RPPI (2010-2021) with Total Value of Dwellings (2022-2025) for ABS-only data
3. Verify data continuity if combining sources
4. Document methodology clearly in indicator.yaml

**Required Action**:
1. Choose data source strategy
2. Download historical data
3. Ensure data is for "all capital cities combined" or create weighted average
4. Format as CSV with date and median price columns

---

## Data Quality Notes

### CPI Data Quality: EXCELLENT
- Complete quarterly series from 2010-2025
- Verified against ABS official data
- Consistent methodology throughout period
- Index values use same base period (2011-12=100)
- Ready for immediate use

### Recent Economic Context (2024-2025)

**Inflation Trends**:
- Peak inflation: 7.83% (December 2022)
- Gradual decline through 2023
- Stabilized around 2.4-3.8% in 2024
- Recent uptick to 3.2% (September 2025)

**Unemployment Trends**:
- Remained relatively stable 2024-2025
- Range: 3.9% - 4.5%
- October 2025: 4.3%

**GDP Growth Trends**:
- Modest quarterly growth in 2024 (0.1-0.6%)
- Average around 0.3% per quarter
- June 2025 showed stronger growth (0.6%)

---

## Next Steps for Complete Data Collection

### Priority 1: Complete Core Economic Indicators
1. **Unemployment Rate** (2010-2023): Download ABS Labour Force time series
2. **GDP Growth** (2010-2023): Download ABS National Accounts time series
3. **Wage Price Index** (2010-2025): Download ABS WPI time series

### Priority 2: Resolve House Price Data
1. Evaluate alternative sources (FRED vs combined ABS sources)
2. Make decision on methodology
3. Download and format data
4. Document source and methodology

### Priority 3: Data Validation
1. Verify all dates are in correct format (YYYY-MM-DD)
2. Check for missing periods
3. Validate data against ABS releases
4. Run `python data.py` validation script

### Priority 4: Create indicator.yaml Files
After data collection is complete, create indicator.yaml for each indicator following the project schema.

---

## How to Download ABS Time Series Data

### General Process:

1. **Navigate to the ABS publication page** for the indicator
2. **Find the "Data downloads" section** (usually in left sidebar or top navigation)
3. **Download the Excel time series spreadsheet** (look for "All time series spreadsheets")
4. **Open the Excel file** and identify the correct table
5. **Locate the relevant columns**:
   - Date column
   - Value column (rate, index, percentage change)
   - Ensure it's the right series (seasonally adjusted vs trend, etc.)
6. **Export to CSV** or manually copy the data
7. **Format dates** as YYYY-MM-DD using end-of-period dates
8. **Verify data** against published media releases

### Common ABS Table Names:

- **CPI**: Table 1 or Table 2 - All Groups CPI
- **Labour Force**: Table 1 - Labour Force Status
- **GDP**: Table 1 - Key National Accounts Aggregates
- **WPI**: Table 1 - Total Hourly Rates of Pay Excluding Bonuses

### Tips:

- ABS often provides multiple Excel sheets in one download
- Look for the "Data1" or "Data" tab in Excel files
- First row is usually column headers
- Dates may need reformatting (ABS uses various formats)
- Some series have both original, seasonally adjusted, and trend - choose seasonally adjusted
- Always verify you have the "All Australia" series, not state-specific

---

## File Naming Convention

### Final CSV Files Should Be Named:
- `data/australia/consumer_price_index/data.csv`
- `data/australia/unemployment_rate/data.csv`
- `data/australia/gdp_growth/data.csv`
- `data/australia/wage_price_index/data.csv`
- `data/australia/median_house_price/data.csv`

---

## Data Currency Requirements

According to project requirements, data must be kept current:

- **Monthly indicators** (Unemployment): Update within 2 weeks of ABS release
- **Quarterly indicators** (CPI, GDP, WPI, House Price): Update within 3 weeks of ABS release

### ABS Release Schedule:

- **CPI**: Published ~3-4 weeks after quarter end (late Jan, Apr, Jul, Oct)
- **Labour Force**: Published mid-month for previous month
- **GDP**: Published ~9 weeks after quarter end (early Mar, Jun, Sep, Dec)
- **WPI**: Published ~7 weeks after quarter end (mid-Feb, May, Aug, Nov)

### Current Data Status (as of November 2025):

✓ CPI: Current through September 2025 (released October 2025)
✓ Unemployment: Current through October 2025 (released November 2025)
✓ GDP: Current through June 2025 (released September 2025)
⚠️ WPI: Need to collect
⚠️ House Prices: Need to collect

---

## Contact Information for API Access

If you want to automate data collection via API:

**ABS API Support**: api.data@abs.gov.au

Available APIs:
- Indicator API: https://indicator.api.abs.gov.au/
- Data API: More flexible for custom queries

Requires API key (free, email to request).
