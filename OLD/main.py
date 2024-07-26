import pandas as pd
import sqlite3
from borsdata_api import BorsdataAPI
from constants import API_KEY, DB_FILE

# Initialize Borsdata API
api = BorsdataAPI(API_KEY)

# Connect to the SQLite database
def connect_db():
    return sqlite3.connect(DB_FILE)

# Function to save price data to the database
def save_price_data_to_db(df, company_id):
    conn = connect_db()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO price_data (company_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, row['date'], row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    conn.close()

# Function to save KPI summary data to the database
def save_kpi_summary_to_db(df, company_id):
    conn = connect_db()
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO kpi_summary (company_id, year, period, kpi_id, kpi_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (company_id, row['year'], row['period'], row['kpiId'], row['kpiValue']))
    conn.commit()
    conn.close()

# Function to fetch and save price data
def fetch_and_save_price_data(company_id, start_date=None, end_date=None):
    prices = api.get_instrument_stock_prices(company_id, from_date=start_date, to_date=end_date)
    df = pd.DataFrame(prices)
    df.rename(columns={'d': 'date', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'}, inplace=True)
    save_price_data_to_db(df, company_id)

# Function to fetch and save KPI summary data
def fetch_and_save_kpi_summary(company_id, report_type):
    kpi_summary = api.get_kpi_summary(company_id, report_type)
    df = pd.DataFrame(kpi_summary).reset_index()
    df['company_id'] = company_id
    save_kpi_summary_to_db(df, company_id)

# Example usage
if __name__ == "__main__":
    company_id = 3  # Example company ID
    fetch_and_save_price_data(company_id, start_date="2022-01-01", end_date="2023-01-01")
    fetch_and_save_kpi_summary(company_id, "quarter")
    print("Data fetched and saved to database.")
