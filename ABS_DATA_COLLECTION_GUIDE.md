# Australian Bureau of Statistics - Data Collection Guide

## Overview

This guide provides instructions for collecting historical economic data from the ABS for the period 2010 to present.

## Data Sources and Collection Methods

### Method 1: Direct Download from ABS Website

Each indicator has downloadable Excel time series files available from the ABS website. Below are the specific URLs and instructions.

### Method 2: ABS Data API

The ABS provides two APIs for programmatic access:
- **Indicator API**: https://indicator.api.abs.gov.au/
- **Data API**: More flexible, allows custom queries

To use the API, you need to:
1. Request an API key by emailing: api.data@abs.gov.au
2. Include the key in request header: `x-api-key: [your-key]`

---

## 1. Consumer Price Index (CPI)

### Source
https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release

### Data Required
- Date (end of quarter: Mar 31, Jun 30, Sep 30, Dec 31)
- Inflation rate (year-over-year percentage change)
- CPI index value (base period 2011-12 = 100)

### Download Instructions
1. Visit the CPI Australia latest release page
2. Look for "Data downloads" section
3. Download the Excel time series spreadsheet
4. Extract Table 1: CPI All Groups Index Numbers and Percentage Changes

### Recent Data Points (2024-2025)
- Dec 2024: 2.4% annual inflation
- Mar 2025: 2.4% annual inflation
- Jun 2025: 2.7% annual inflation (trimmed mean)
- Sep 2025: 3.2% annual inflation

### API Dataflow
- Dataflow ID: `CPI_H`

---

## 2. Unemployment Rate

### Source
https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release

### Data Required
- Date (end of month)
- Seasonally adjusted unemployment rate (percentage)

### Download Instructions
1. Visit the Labour Force Australia latest release page
2. Look for "Data downloads" section
3. Download the Excel time series spreadsheet (Catalogue 6202.0)
4. Extract Table 1: Labour Force Status by Sex - Seasonally Adjusted
5. Use the unemployment rate column

### Recent Data Points (2024-2025)
- Jan 2024: Available from ABS
- Feb 2025: 4.1%
- Sep 2025: 4.5%
- Oct 2025: 4.3%
- Dec 2024: 4.0%

### API Dataflow
- Dataflow ID: Labour Force related dataflows

---

## 3. GDP Growth

### Source
https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release

### Data Required
- Date (end of quarter)
- Quarter-on-quarter GDP growth rate (percentage)

### Download Instructions
1. Visit the Australian National Accounts latest release page
2. Look for "Data downloads" section
3. Download the Excel time series spreadsheet
4. Extract Table 1: Key Aggregates - Seasonally Adjusted
5. Use the GDP chain volume measures percentage change column

### Recent Data Points (2024-2025)
- Mar 2024: 0.1%
- Jun 2024: 0.2%
- Sep 2024: 0.3%
- Dec 2024: 0.6%
- Mar 2025: 0.2%
- Jun 2025: 0.6%

### API Dataflow
- Dataflow ID: `GDP`

---

## 4. Wage Price Index

### Source
https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release

### Data Required
- Date (end of quarter)
- Annual wage growth (year-over-year percentage change)
- Wage Price Index value (base period 2008-09 = 100)

### Download Instructions
1. Visit the Wage Price Index Australia latest release page
2. Look for "Data downloads" section
3. Download the Excel time series spreadsheet
4. Extract Total Hourly Rates of Pay Excluding Bonuses - All Sectors
5. Use both the index and percentage change columns

### API Dataflow
- Dataflow ID: Wage Price Index related dataflows

---

## 5. Median House Price

### Source
**Primary (Historical)**: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities
**Note**: This publication ceased in December 2021

**Current Alternative**: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release

### Data Required
- Date (end of quarter)
- Median dwelling price for all capital cities combined (AUD)

### Download Instructions

#### For Historical Data (2010-2021)
1. Visit the Residential Property Price Indexes page
2. Access archived releases
3. Download time series data up to December 2021

#### For Current Data (2022-Present)
1. Visit the Total Value of Dwellings page
2. Download the latest release data
3. Extract median price data for all capital cities

#### Alternative Source
Federal Reserve Economic Data (FRED) provides Real Residential Property Prices for Australia:
- URL: https://fred.stlouisfed.org/series/QAUR628BIS
- Coverage: Q1 1970 to Q2 2025
- Format: Downloadable CSV

---

## Data Formatting Guidelines

### Date Format
All dates must be in ISO 8601 format: `YYYY-MM-DD`

### End of Period Dates
- **Quarterly**: Use last day of quarter
  - March: `YYYY-03-31`
  - June: `YYYY-06-30`
  - September: `YYYY-09-30`
  - December: `YYYY-12-31`
- **Monthly**: Use last day of month
  - January: `YYYY-01-31`
  - February: `YYYY-02-28` or `YYYY-02-29` (leap years)
  - etc.

### CSV Structure
- First row: Column headers matching schema
- Data in chronological order
- Missing values: Leave blank (not "N/A")
- Decimal places: Use appropriate precision (2-3 decimal places for percentages)

---

## Validation

After collecting data, run:
```bash
python data.py
```

Ensure no ERROR messages appear before committing.

---

## Notes

### Data Currency
According to project requirements:
- Monthly indicators: Update within 2 weeks of release
- Quarterly indicators: Update within 3 weeks of release
- Avoid stale data (data more than one period old is unacceptable)

### ABS Release Schedule
- CPI: Quarterly (late January, April, July, October)
- Labour Force: Monthly (mid-month for previous month)
- GDP: Quarterly (early March, June, September, December)
- Wage Price Index: Quarterly (mid-February, May, August, November)

### Historical Data Quality
When compiling data from 2010:
- Check for methodology changes
- Note any data revisions
- Ensure consistent series (watch for rebenchmarking)
- Verify base periods for index values
