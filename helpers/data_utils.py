import pandas as pd

def fetch_and_save_monthly_price_data(api, ins_id, start_date=None, end_date=None):
    """
    Fetches and aggregates daily stock prices into monthly data.
    """
    print(f"Fetching monthly price data for instrument {ins_id}...")
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
    print(f"Monthly price data for instrument {ins_id} fetched and aggregated.")
    return monthly_df

def fetch_and_save_report_data(api, ins_id):
    """
    Fetches quarterly and yearly report data for the specified instrument.
    """
    print(f"Fetching report data for instrument {ins_id}...")
    quarters, years = api.get_instrument_reports(ins_id)[:2]
    combined_df = pd.concat([quarters, years], ignore_index=True)
    combined_df.reset_index(inplace=True)
    for date_col in ['reportStartDate', 'reportEndDate', 'reportDate']:
        if date_col in combined_df.columns:
            combined_df[date_col] = pd.to_datetime(date_col).dt.strftime('%Y-%m-%d')
    print(f"Report data for instrument {ins_id} fetched and combined.")
    return combined_df

def fetch_instrument_list(api):
    """
    Fetches the list of instruments from the Borsdata API.
    """
    print("Fetching instrument list...")
    df = api.get_instruments()
    print(f"Fetched {len(df.index)} instruments.")
    return df.index.tolist()
