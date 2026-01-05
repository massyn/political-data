# Data Collection Index

Quick reference guide to all data collection files and resources.

## Complete Data Files (Ready to Use)

### 1. Consumer Price Index
- **File**: `CPI_DATA_2010_2025.csv` (1.5 KB)
- **Coverage**: Q1 2010 - Q3 2025 (63 quarters)
- **Status**: ✓ COMPLETE
- **Format**: date, value (inflation %), index (base 2011-12=100)

### 2. House Price Index
- **File**: `HOUSE_PRICE_DATA_FRED_2010_2025.csv` (1.3 KB)
- **Coverage**: Q1 2010 - Q2 2025 (62 quarters)
- **Status**: ✓ COMPLETE
- **Format**: date, value (real price index)
- **Note**: Index values, not dollar amounts

## Sample Data Files (Need Completion)

### 3. Unemployment Rate
- **File**: `UNEMPLOYMENT_DATA_SAMPLE_2024_2025.csv` (364 bytes)
- **Coverage**: Jan 2024 - Oct 2025 (22 months)
- **Status**: ⚠️ 13% COMPLETE
- **Missing**: Jan 2010 - Dec 2023 (168 months)

### 4. GDP Growth
- **File**: `GDP_GROWTH_DATA_SAMPLE_2024_2025.csv` (108 bytes)
- **Coverage**: Q1 2024 - Q2 2025 (6 quarters)
- **Status**: ⚠️ 10% COMPLETE
- **Missing**: Q1 2010 - Q4 2023 (56 quarters)

### 5. Wage Price Index
- **File**: Not yet created
- **Status**: ❌ NOT COLLECTED
- **Required**: Q1 2010 - latest quarter (~62 quarters)

## Documentation Files

### Primary Documentation
1. **FINAL_DATA_COLLECTION_REPORT.md** (17 KB)
   - Complete status report
   - Data quality assessments
   - Next steps and action items
   - **START HERE** for overview

2. **ABS_DATA_COLLECTION_GUIDE.md** (6.3 KB)
   - Step-by-step download instructions
   - Direct links to all ABS sources
   - API access information
   - Data formatting guidelines

3. **DATA_COLLECTION_SUMMARY.md** (9.8 KB)
   - Detailed status for each indicator
   - Alternative data sources
   - Validation requirements
   - File naming conventions

4. **DATA_COLLECTION_INDEX.md** (this file)
   - Quick reference to all files
   - File sizes and coverage
   - Navigation guide

## Tools and Scripts

### Python Script
- **File**: `abs_data_fetcher.py` (7.9 KB)
- **Purpose**: Automated data collection from FRED and ABS
- **Requirements**: pandas, requests, openpyxl
- **Usage**: `python abs_data_fetcher.py`
- **Features**:
  - FRED API data fetching (working)
  - Date formatting utilities
  - CSV export functions
  - Inflation rate calculator

### Validation Script (Existing)
- **File**: `data.py` (6.1 KB)
- **Purpose**: Validate data structure and indicator.yaml files
- **Usage**: `python data.py`
- **Run before**: Committing any data changes

## Quick Start Guide

### To Use Complete Data Immediately

1. Copy complete data files to project structure:
   ```bash
   mkdir -p data/australia/consumer_price_index
   mkdir -p data/australia/median_house_price
   cp CPI_DATA_2010_2025.csv data/australia/consumer_price_index/data.csv
   cp HOUSE_PRICE_DATA_FRED_2010_2025.csv data/australia/median_house_price/data.csv
   ```

2. Create indicator.yaml files (follow schema in `.claude/CLAUDE.md`)

3. Validate:
   ```bash
   python data.py
   ```

### To Complete Missing Data

1. Read: `ABS_DATA_COLLECTION_GUIDE.md`
2. Follow instructions for each indicator
3. Download Excel files from ABS
4. Format as CSV
5. Merge with existing sample data
6. Validate with `python data.py`

### To Automate Collection (Advanced)

1. Request ABS API key: api.data@abs.gov.au
2. Store in `.env` file
3. Modify `abs_data_fetcher.py` to use API
4. Run automated collection

## File Size Summary

| File | Size | Type |
|------|------|------|
| CPI_DATA_2010_2025.csv | 1.5 KB | Data (Complete) |
| HOUSE_PRICE_DATA_FRED_2010_2025.csv | 1.3 KB | Data (Complete) |
| UNEMPLOYMENT_DATA_SAMPLE_2024_2025.csv | 364 B | Data (Sample) |
| GDP_GROWTH_DATA_SAMPLE_2024_2025.csv | 108 B | Data (Sample) |
| FINAL_DATA_COLLECTION_REPORT.md | 17 KB | Documentation |
| DATA_COLLECTION_SUMMARY.md | 9.8 KB | Documentation |
| abs_data_fetcher.py | 7.9 KB | Tool |
| ABS_DATA_COLLECTION_GUIDE.md | 6.3 KB | Documentation |

**Total Data Collected**: 3.2 KB (2 complete indicators)
**Total Documentation**: 40.1 KB
**Total Tools**: 7.9 KB

## Data Coverage Timeline

```
2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
CPI:          ████████████████████████████████████████████████████████████████  ✓
House:        ████████████████████████████████████████████████████████████████  ✓
Unemployment: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████  ⚠️
GDP:          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████  ⚠️
WPI:          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ❌

Legend: █ Complete | ░ Missing | ✓ Ready | ⚠️ Partial | ❌ Not Collected
```

## Data Sources Reference

| Indicator | Official Source | Alternative Source |
|-----------|----------------|-------------------|
| CPI | ABS | RBA, rateinflation.com |
| House Price | ABS (discontinued 2021) | FRED (BIS data) ✓ |
| Unemployment | ABS Labour Force | FRED, Trading Economics |
| GDP | ABS National Accounts | FRED, Trading Economics |
| WPI | ABS | - |

## Next Actions Checklist

- [ ] Download ABS unemployment time series (Jan 2010-Dec 2023)
- [ ] Download ABS GDP time series (Q1 2010-Q4 2023)
- [ ] Download ABS WPI time series (Q1 2010-latest)
- [ ] Create indicator.yaml for CPI
- [ ] Create indicator.yaml for House Price Index
- [ ] Create indicator.yaml for Unemployment
- [ ] Create indicator.yaml for GDP
- [ ] Create indicator.yaml for WPI
- [ ] Organize files into data/australia/ structure
- [ ] Run validation: `python data.py`
- [ ] Update data with latest releases (check ABS schedule)
- [ ] Consider setting up automated updates

## Estimated Completion Time

- **Manual collection**: 2 hours
- **With automation**: 2 hours + API key wait time

## Support Resources

- ABS Website: https://www.abs.gov.au
- ABS Phone: 1300 135 070
- API Support: api.data@abs.gov.au
- FRED Database: https://fred.stlouisfed.org

## Version History

- **2025-11-16**: Initial data collection
  - CPI: Complete (63 quarters)
  - House Prices: Complete (62 quarters, FRED source)
  - Unemployment: Sample (22 months)
  - GDP: Sample (6 quarters)
  - WPI: Not collected
