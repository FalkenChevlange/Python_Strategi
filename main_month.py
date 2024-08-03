import pandas as pd
import numpy as np

def connect_db():
    import sqlite3
    from borsdata_api.constants import DB_FILE_MONTHLY
    return sqlite3.connect(DB_FILE_MONTHLY)

def fetch_instrument_list():
    # Simulerad funktion för att hämta instrumentlistan - ersätt med din API-anrop
    return list(range(1, 101))  # Returnerar en lista med instrument-ID:n från 1 till 100

def fetch_and_save_monthly_price_data(ins_id, start_date="2000-01-01", end_date="2024-07-01"):
    # Simulerad funktion för att hämta data - ersätt med din API-anrop
    def fetch_monthly_data(ins_id, start_date, end_date):
        # Simulerad API-svar
        return pd.DataFrame({
            "date": pd.date_range(start_date, end_date, freq='M'),
            "close": np.random.random(size=12)
        })
    
    print(f"Fetching monthly price data for instrument ID {ins_id}")
    df = fetch_monthly_data(ins_id, start_date, end_date)
    
    if 'date' not in df.columns:
        print(f"Warning: 'date' column is missing for instrument ID {ins_id}. Skipping this instrument.")
        return
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Spara data till databasen
    conn = connect_db()
    df.to_sql('monthly_price_data', conn, if_exists='append', index=False)
    conn.close()
    print(f"Monthly price data for instrument ID {ins_id} saved to database.")

def fetch_and_save_report_data(ins_id):
    # Simulerad funktion för att hämta rapportdata - ersätt med din API-anrop
    def fetch_report_data(ins_id):
        # Simulerad API-svar
        return pd.DataFrame({
            "report_date": pd.date_range("2000-01-01", periods=4, freq='A'),
            "revenue": np.random.random(size=4)
        })
    
    print(f"Fetching report data for instrument ID {ins_id}")
    df = fetch_report_data(ins_id)
    
    if 'report_date' not in df.columns:
        print(f"Warning: 'report_date' column is missing for instrument ID {ins_id}. Skipping this instrument.")
        return
    
    df['report_date'] = pd.to_datetime(df['report_date'])
    
    # Spara data till databasen
    conn = connect_db()
    df.to_sql('report_data', conn, if_exists='append', index=False)
    conn.close()
    print(f"Report data for instrument ID {ins_id} saved to database.")

if __name__ == "__main__":
    print("Starting data fetch process.")
    instrument_ids = fetch_instrument_list()  # Fetch data for all instruments
    for ins_id in instrument_ids:
        fetch_and_save_monthly_price_data(ins_id, start_date="2000-01-01", end_date="2024-07-01")
        fetch_and_save_report_data(ins_id)
    print("Monthly data fetched and saved to database for all instruments.")
