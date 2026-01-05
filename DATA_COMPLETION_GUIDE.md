# Data Completion Guide

## Progress Summary

I've successfully updated the following indicators with historical data back to 2010:

### ✅ Completed
1. **RBA Cash Rate** - Complete from 2010-2025 (38 data points)
2. **Consumer Price Index** - Complete from 2010-2025 (64 quarters)

### ⚠️ Still Missing Data (2010-2019/2020)
3. **Unemployment Rate** - Currently starts 2020-01-31
4. **GDP Growth** - Currently starts 2019-12-31
5. **Wage Price Index** - Currently starts 2020-03-31
6. **Median House Price** - Currently starts 2020-03-31
7. **Emergency Department Wait Times** - Currently starts 2015-06-30

## Current Missing Data Status

Based on the Government Scorecard:
- **Anthony Albanese (2025, current)**: 0 missing ✓
- **Anthony Albanese (2022)**: 0 missing ✓
- **Scott Morrison (2019)**: 0 missing ✓
- **Malcolm Turnbull (2016)**: 5 missing (needs data back to 2016)
- **Tony Abbott (2013)**: 4 missing (needs data back to 2013)

## How to Complete the Missing Data

### 1. Unemployment Rate (Monthly, 2010-2019)

**Source**: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release

**Steps**:
1. Visit the URL above
2. Scroll to "Data downloads" section
3. Download "Table 1. Labour force status by Sex, Australia - Seasonally adjusted" (Excel file)
4. Open the file and find the "Unemployment rate" row
5. Copy monthly values from **January 2010 to December 2019**
6. Format as: `YYYY-MM-DD` (last day of month), `value` (percentage)

**Expected format**:
```csv
date,value
2010-01-31,5.3
2010-02-28,5.3
...
2019-12-31,5.1
```

**File to update**: `data/Australia/unemployment_rate/data.csv`

---

### 2. GDP Growth (Quarterly, 2010-2019)

**Source**: https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release

**Steps**:
1. Visit the URL above
2. Scroll to "Data downloads" section
3. Download "Table 1. Key National Accounts Aggregates" (Excel file)
4. Find "GDP - Percentage Change from Previous Quarter" (chain volume measures, seasonally adjusted)
5. Copy quarterly values from **March 2010 to December 2019**
6. Format as: `YYYY-MM-DD` (last day of quarter), `value` (percentage)

**Expected format**:
```csv
date,value
2010-03-31,0.5
2010-06-30,1.2
...
2019-09-30,0.5
```

**File to update**: `data/Australia/gdp_growth/data.csv`

---

### 3. Wage Price Index (Quarterly, 2010-2019)

**Source**: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release

**Steps**:
1. Visit the URL above
2. Scroll to "Data downloads" section
3. Download "Table 1. Total Hourly Rates of Pay Excluding Bonuses: Sector, Original, Seasonally Adjusted and Trend" (Excel file)
4. Find two values for "All sectors":
   - **Percentage change from corresponding quarter of previous year** (for `value`)
   - **Index** (base 2008-09=100) (for `index`)
5. Copy quarterly values from **March 2010 to December 2019**
6. Format as: `YYYY-MM-DD` (last day of quarter), `value` (annual %), `index`

**Expected format**:
```csv
date,value,index
2010-03-31,3.5,107.2
2010-06-30,3.3,107.8
...
2019-12-31,2.2,121.5
```

**File to update**: `data/Australia/wage_price_index/data.csv`

---

### 4. Median House Price (Quarterly, 2010-2019)

**Source**: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/latest-release

**Challenge**: The ABS provides a *price index*, not median dollar values. We need actual median prices in AUD.

**Alternative Sources**:
- **CoreLogic**: Historical median house price data (commercial)
- **Domain/REA**: May have historical data available
- **RBA Chart Pack**: Sometimes includes median dwelling prices

**Steps**:
1. Visit the ABS source above or search for "Australia median house price historical data"
2. Look for "Total (8 capital cities)" median dwelling price in AUD
3. Collect quarterly data from **March 2010 to December 2019**
4. Format as: `YYYY-MM-DD` (last day of quarter), `value` (AUD median price)

**Expected format**:
```csv
date,value
2010-03-31,450000
2010-06-30,455000
...
2019-12-31,650000
```

**File to update**: `data/Australia/median_house_price/data.csv`

**Note**: If only index data is available, you may need to use the RPPI (Residential Property Price Index) instead and update the indicator.yaml to reflect that it's an index rather than a dollar value.

---

### 5. Emergency Department Wait Times (Annual, 2010-2014)

**Source**: https://www.aihw.gov.au/hospitals/topics/emergency-departments/time-spent-in-emergency

**Steps**:
1. Visit the URL above
2. Look for historical emergency department data reports
3. Find "Percentage of presentations completed within 4 hours" for financial years
4. Collect data for **2010-11, 2011-12, 2012-13, 2013-14, 2014-15**
5. Format as: `YYYY-06-30` (last day of financial year), `value` (percentage)

**Expected format**:
```csv
date,value
2010-06-30,75
2011-06-30,74
...
2014-06-30,73
```

**File to update**: `data/Australia/emergency_department_wait_times/data.csv`

---

## Data Validation

After updating each file:

1. **Check date format**: All dates must be `YYYY-MM-DD`
2. **Check values**: Ensure no missing values or anomalies
3. **Run validation**: `python data.py`
4. **Test build**: `python build.py`
5. **Check scorecard**: Open `dist/australia.html` and verify missing data counts have decreased

## Target Outcome

When all data is complete, the Government Scorecard should show:
- **All governments**: 0 missing data points
- Complete historical coverage back to 2010 for all economic indicators

## Time Estimate

- **Unemployment Rate**: 15 minutes (120 monthly values)
- **GDP Growth**: 10 minutes (40 quarterly values)
- **Wage Price Index**: 10 minutes (40 quarterly values)
- **Median House Price**: 20 minutes (40 quarterly values, may need alternative source)
- **ED Wait Times**: 10 minutes (5 annual values)

**Total**: ~65 minutes to complete all missing data

## Notes

- ABS Excel files can be large; focus on finding the specific table/row you need
- Seasonally adjusted values are preferred for unemployment and GDP
- Original (not seasonally adjusted) values are typically used for CPI and WPI
- When in doubt, refer to the existing data format in each CSV file as a template
