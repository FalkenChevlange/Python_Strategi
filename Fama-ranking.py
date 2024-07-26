import pandas as pd
import numpy as np
import sqlite3
from borsdata_api.constants import DB_FILE_MONTHLY

# Connect to the SQLite database for monthly data
def connect_db():
    return sqlite3.connect(DB_FILE_MONTHLY)

def calculate_rolling_factors(report_df):
    # Ensure 'report_start_date' is in datetime format
    report_df['report_start_date'] = pd.to_datetime(report_df['report_start_date'])

    # Calculate rolling 4-quarter (12-month) values
    report_df = report_df.sort_values(by=['ins_id', 'report_start_date'])
    report_df['rolling_revenues'] = report_df.groupby('ins_id')['revenues'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_gross_income'] = report_df.groupby('ins_id')['gross_income'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_operating_income'] = report_df.groupby('ins_id')['operating_income'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_earnings_per_share'] = report_df.groupby('ins_id')['earnings_per_share'].rolling(4).sum().reset_index(level=0, drop=True)

    return report_df

def calculate_factors(price_df, report_df):
    # Ensure 'date' columns exist and are in datetime format
    price_df['date'] = pd.to_datetime(price_df['date'])
    report_df['date'] = report_df['report_start_date']
    
    # Merge price and report data
    df = pd.merge(price_df, report_df, on=['ins_id', 'date'], how='left')
    
    # Calculate necessary factors
    df['market_cap'] = df['close'] * df['number_of_shares']
    df['value'] = df['rolling_earnings_per_share'] / df['close']
    df['profitability'] = df['rolling_operating_income'] / df['rolling_gross_income']
    df['momentum'] = df.groupby('ins_id')['close'].pct_change(periods=12)
    df['volatility'] = df.groupby('ins_id')['close'].rolling(window=12).std().reset_index(level=0, drop=True)
    
    return df

def rank_factors(df):
    df['size_rank'] = df.groupby('date')['market_cap'].rank(pct=True)
    df['value_rank'] = df.groupby('date')['value'].rank(pct=True)
    df['profitability_rank'] = df.groupby('date')['profitability'].rank(pct=True)
    df['momentum_rank'] = df.groupby('date')['momentum'].rank(pct=True)
    df['volatility_rank'] = df.groupby('date')['volatility'].rank(pct=True, ascending=False)
    
    return df

def save_rankings_to_db(df):
    conn = connect_db()
    ranking_df = df[['ins_id', 'date', 'size_rank', 'value_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']]
    ranking_df.to_sql('factor_rankings', conn, if_exists='replace', index=False)
    conn.close()
    print("Factor rankings saved to database.")

def main():
    conn = connect_db()
    
    # Read monthly price and report data from the database
    price_df = pd.read_sql_query("SELECT * FROM monthly_price_data", conn)
    report_df = pd.read_sql_query("SELECT * FROM monthly_report_data", conn)
    
    # Calculate rolling factors and rank them
    rolling_report_df = calculate_rolling_factors(report_df)
    factors_df = calculate_factors(price_df, rolling_report_df)
    ranked_df = rank_factors(factors_df)
    
    # Save the ranked factors to the database
    save_rankings_to_db(ranked_df)

    conn.close()

if __name__ == "__main__":
    main()
