import pandas as pd
import numpy as np

def calculate_portfolio_returns(df, factor, holding_period='quarterly'):
    if factor not in df.columns:
        raise ValueError(f"Factor '{factor}' not found in DataFrame columns")
        
    df = df.sort_values(by=['date', factor])
    df['rank'] = df.groupby('date', observed=True)[factor].rank(pct=True)
    df['portfolio'] = pd.cut(df['rank'], bins=4, labels=[1, 2, 3, 4])
    
    df['return'] = df.groupby('ins_id', observed=True)['close'].pct_change()
    
    holding_period_map = {
        'quarterly': 3,
        'yearly': 12,
        '2_years': 24,
        '3_years': 36,
        '5_years': 60
    }

    if holding_period in holding_period_map:
        period_months = holding_period_map[holding_period]
        df['holding_return'] = df.groupby('ins_id', observed=True)['return'].rolling(period_months).apply(lambda x: np.prod(1 + x) - 1).reset_index(level=0, drop=True)
    
    portfolio_returns = df.groupby(['date', 'portfolio'], observed=True)['holding_return'].mean().reset_index()
    return portfolio_returns, df
