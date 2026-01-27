"""
ABS Data Fetcher

This script provides helper functions to fetch Australian Bureau of Statistics data.
Note: Some functionality requires direct file downloads from ABS website.

Requirements:
    pip install requests pandas openpyxl

Usage:
    python abs_data_fetcher.py
"""

import requests
import pandas as pd
from datetime import datetime
import os


class ABSDataFetcher:
    """Helper class to fetch ABS data from various sources"""

    def __init__(self):
        self.base_url = "https://www.abs.gov.au"
        self.api_key = os.getenv('ABS_API_KEY')  # Store API key in .env file

    def fetch_cpi_from_rateinflation(self):
        """
        Fetch historical CPI data from rateinflation.com
        Returns a pandas DataFrame with date, index, and calculated inflation rate
        """
        print("Fetching CPI data from rateinflation.com...")

        # This is a simplified example - actual implementation would scrape the table
        # or use an API if available

        # For now, return the data we've already collected
        data = {
            'date': [],
            'index': [],
            'value': []
        }

        # Note: In practice, you'd want to scrape or fetch this data programmatically
        # The data is available but requires web scraping

        print("Note: Web scraping implementation needed for automated fetch")
        print("Please use the manually collected CPI_DATA_2010_2025.csv file")

        return pd.DataFrame(data)

    def fetch_from_fred(self, series_id, start_date='2010-01-01'):
        """
        Fetch data from FRED (Federal Reserve Economic Data)

        Args:
            series_id: FRED series ID (e.g., 'QAUR628BIS' for Australian house prices)
            start_date: Start date in YYYY-MM-DD format

        Returns:
            pandas DataFrame with date and value columns
        """
        print(f"Fetching FRED series {series_id}...")

        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

        try:
            df = pd.read_csv(url)
            # FRED CSVs typically have columns named 'DATE' or 'date' and the series ID
            # Rename columns to standardized names
            df.columns = ['date', 'value']
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= start_date]
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')

            # Remove any rows with missing values
            df = df.dropna()

            print(f"Successfully fetched {len(df)} data points")
            return df

        except Exception as e:
            print(f"Error fetching FRED data: {e}")
            return pd.DataFrame()

    def calculate_inflation_rate(self, cpi_index_series):
        """
        Calculate year-over-year inflation rate from CPI index values

        Args:
            cpi_index_series: pandas Series with CPI index values

        Returns:
            pandas Series with inflation rates (%)
        """
        # Calculate year-over-year percentage change
        # For quarterly data, this means comparing to 4 quarters ago
        inflation = cpi_index_series.pct_change(periods=4) * 100
        return inflation.round(2)

    def format_quarter_end_date(self, year, quarter):
        """
        Convert year and quarter to end-of-quarter date

        Args:
            year: Year (e.g., 2024)
            quarter: Quarter number (1, 2, 3, or 4)

        Returns:
            Date string in YYYY-MM-DD format
        """
        quarter_end_months = {1: '03-31', 2: '06-30', 3: '09-30', 4: '12-31'}
        return f"{year}-{quarter_end_months[quarter]}"

    def format_month_end_date(self, year, month):
        """
        Convert year and month to end-of-month date

        Args:
            year: Year (e.g., 2024)
            month: Month number (1-12)

        Returns:
            Date string in YYYY-MM-DD format
        """
        # Get last day of month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        from datetime import timedelta
        last_day = next_month - timedelta(days=1)

        return last_day.strftime('%Y-%m-%d')

    def save_to_csv(self, df, filename, columns=None):
        """
        Save DataFrame to CSV file

        Args:
            df: pandas DataFrame
            filename: Output filename
            columns: Optional list of column names to use
        """
        if columns:
            df.columns = columns

        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")


def main():
    """Main function to demonstrate usage"""

    fetcher = ABSDataFetcher()

    # Example 1: Fetch Australian house price data from FRED
    print("\n=== Fetching House Price Data from FRED ===")
    house_prices = fetcher.fetch_from_fred('QAUR628BIS', start_date='2010-01-01')

    if not house_prices.empty:
        # Convert quarterly data to end-of-quarter dates
        # FRED data comes with quarterly dates at start of quarter, convert to end
        house_prices['date'] = pd.to_datetime(house_prices['date'])

        # Convert to end of quarter
        house_prices['date'] = house_prices['date'] + pd.offsets.QuarterEnd(0)
        house_prices['date'] = house_prices['date'].dt.strftime('%Y-%m-%d')

        print(f"\nFirst few rows:\n{house_prices.head()}")
        print(f"Last few rows:\n{house_prices.tail()}")

        # Save to CSV
        fetcher.save_to_csv(house_prices, 'HOUSE_PRICE_DATA_FRED_2010_2025.csv')
        print("\nNote: This is Real Residential Property Price Index from FRED/BIS")
        print("Values are index numbers (not dollar amounts)")
        print("For actual median prices in AUD, use ABS Total Value of Dwellings data")

    # Example 2: Calculate inflation from CPI index
    print("\n=== Calculating Inflation Rates ===")

    # Load the CPI data we already have
    try:
        cpi_data = pd.read_csv('CPI_DATA_2010_2025.csv')
        print(f"Loaded {len(cpi_data)} CPI data points")
        print(f"\nRecent data:\n{cpi_data.tail(10)}")

    except FileNotFoundError:
        print("CPI_DATA_2010_2025.csv not found")

    # Example 3: Demonstrate date formatting
    print("\n=== Date Formatting Examples ===")
    print(f"Q1 2024 end date: {fetcher.format_quarter_end_date(2024, 1)}")
    print(f"Q2 2024 end date: {fetcher.format_quarter_end_date(2024, 2)}")
    print(f"January 2024 end date: {fetcher.format_month_end_date(2024, 1)}")
    print(f"February 2024 end date: {fetcher.format_month_end_date(2024, 2)}")

    print("\n=== Instructions for Manual Data Collection ===")
    print("""
    For ABS data that requires manual download:

    1. Unemployment Rate:
       - Visit: https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release
       - Download Excel time series
       - Extract seasonally adjusted unemployment rate
       - Use monthly end dates

    2. GDP Growth:
       - Visit: https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/latest-release
       - Download Excel time series
       - Extract quarterly GDP growth (chain volume, seasonally adjusted)
       - Use quarter end dates

    3. Wage Price Index:
       - Visit: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/latest-release
       - Download Excel time series
       - Extract Total Hourly Rates of Pay Excluding Bonuses
       - Use quarter end dates

    For API access:
       - Email api.data@abs.gov.au to request API key
       - Store in .env file as ABS_API_KEY
       - Use ABS Indicator API or Data API
    """)


if __name__ == "__main__":
    main()
