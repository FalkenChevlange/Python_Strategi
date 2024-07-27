import pandas as pd
import numpy as np

def calculate_rolling_factors(report_df):
    report_df['report_start_date'] = pd.to_datetime(report_df['report_start_date'])
    report_df = report_df.sort_values(by=['ins_id', 'report_start_date'])
    report_df['rolling_revenues'] = report_df.groupby('ins_id')['revenues'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_gross_income'] = report_df.groupby('ins_id')['gross_income'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_operating_income'] = report_df.groupby('ins_id')['operating_income'].rolling(4).sum().reset_index(level=0, drop=True)
    report_df['rolling_earnings_per_share'] = report_df.groupby('ins_id')['earnings_per_share'].rolling(4).sum().reset_index(level=0, drop=True)
    return report_df

def calculate_factors(price_df, report_df):
    price_df['date'] = pd.to_datetime(price_df['date'])
    report_df['date'] = report_df['report_start_date']
    df = pd.merge(price_df, report_df, on=['ins_id', 'date'], how='left')
    df['market_cap'] = df['close'] * df['number_of_shares']
    
    # Updated value factor calculation
    df['operating_earnings_per_share'] = df['rolling_operating_income'] / df['number_of_shares']
    df['value_factor'] = df['operating_earnings_per_share'] / df['close']
    
    df['profitability'] = df['rolling_operating_income'] / df['rolling_gross_income']
    df['momentum'] = df.groupby('ins_id')['close'].pct_change(periods=12)
    df['volatility'] = df.groupby('ins_id')['close'].rolling(window=12).std().reset_index(level=0, drop=True)
    return df
