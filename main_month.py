import pandas as pd
import sqlite3
from borsdata_api.borsdata_api import BorsdataAPI
from borsdata_api.constants import API_KEY, DB_FILE_MONTHLY

# Initialize Borsdata API
api = BorsdataAPI(API_KEY)

# Connect to the SQLite database
def connect_db():
    return sqlite3.connect(DB_FILE_MONTHLY)

# Function to save price data to the database
def save_price_data_to_db(df, ins_id):
    conn = connect_db()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO monthly_price_data (ins_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ins_id, row['date'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    conn.close()
    print(f"Monthly price data for ins_id {ins_id} saved to database.")

# Function to save report data to the database
def save_report_data_to_db(df, ins_id):
    conn = connect_db()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO monthly_report_data (
                ins_id, year, period, revenues, gross_income, operating_income, profit_before_tax, profit_to_equity_holders,
                earnings_per_share, number_of_shares, dividend, intangible_assets, tangible_assets, financial_assets,
                non_current_assets, cash_and_equivalents, current_assets, total_assets, total_equity, non_current_liabilities,
                current_liabilities, total_liabilities_and_equity, net_debt, cash_flow_from_operating_activities,
                cash_flow_from_investing_activities, cash_flow_from_financing_activities, cash_flow_for_the_year,
                free_cash_flow, stock_price_average, stock_price_high, stock_price_low, report_start_date,
                report_end_date, broken_fiscal_year, currency, currency_ratio, net_sales, report_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ins_id, row.get('year', None), row.get('period', None), row.get('revenues', None), row.get('grossIncome', None), row.get('operatingIncome', None),
            row.get('profitBeforeTax', None), row.get('profitToEquityHolders', None), row.get('earningsPerShare', None), row.get('numberOfShares', None),
            row.get('dividend', None), row.get('intangibleAssets', None), row.get('tangibleAssets', None), row.get('financialAssets', None), row.get('nonCurrentAssets', None),
            row.get('cashAndEquivalents', None), row.get('currentAssets', None), row.get('totalAssets', None), row.get('totalEquity', None), row.get('nonCurrentLiabilities', None),
            row.get('currentLiabilities', None), row.get('totalLiabilitiesAndEquity', None), row.get('netDebt', None), row.get('cashFlowFromOperatingActivities', None),
            row.get('cashFlowFromInvestingActivities', None), row.get('cashFlowFromFinancingActivities', None), row.get('cashFlowForTheYear', None),
            row.get('freeCashFlow', None), row.get('stockPriceAverage', None), row.get('stockPriceHigh', None), row.get('stockPriceLow', None),
            row.get('reportStartDate', None), row.get('reportEndDate', None),
            row.get('brokenFiscalYear', None), row.get('currency', None), row.get('currencyRatio', None), row.get('netSales', None), row.get('reportDate', None)
        ))
    conn.commit()
    conn.close()
    print(f"Report data for ins_id {ins_id} saved to database.")

# Function to fetch and save monthly price data
def fetch_and_save_monthly_price_data(ins_id, start_date=None, end_date=None):
    df = api.get_instrument_stock_prices(ins_id, from_date=start_date, to_date=end_date)
    df.reset_index(inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    
    # Aggregate daily data to monthly data
    monthly_df = df.resample('MS', on='date').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).reset_index()
    
    monthly_df['date'] = monthly_df['date'].dt.strftime('%Y-%m-%d')
    save_price_data_to_db(monthly_df, ins_id)

# Function to fetch and save report data
def fetch_and_save_report_data(ins_id):
    quarters, years = api.get_instrument_reports(ins_id)[:2]  # Only fetch quarters and years
    for df in [quarters, years]:
        df.reset_index(inplace=True)  # Ensure the index is reset
        for date_col in ['reportStartDate', 'reportEndDate', 'reportDate']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
        print(df.head())  # Debug: Print the DataFrame
        print(df.columns)  # Debug: Print the DataFrame columns
        save_report_data_to_db(df, ins_id)

# Function to fetch instrument list
def fetch_instrument_list():
    df = api.get_instruments()
    return df.index.tolist()  # Assuming the instrument IDs are in the index

# Example usage
if __name__ == "__main__":
    instrument_ids = fetch_instrument_list()[:40]  # Fetch data for the first 5 instruments by default
    for ins_id in instrument_ids:
        fetch_and_save_monthly_price_data(ins_id, start_date="2000-01-01", end_date="2024-07-01")
        fetch_and_save_report_data(ins_id)
    print("Monthly data fetched and saved to database for all instruments.")
