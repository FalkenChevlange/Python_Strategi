def rank_factors(df):
    df['size_rank'] = df.groupby('date')['market_cap'].rank(pct=True)
    df['value_rank'] = df.groupby('date')['value'].rank(pct=True)
    df['profitability_rank'] = df.groupby('date')['profitability'].rank(pct=True)
    df['momentum_rank'] = df.groupby('date')['momentum'].rank(pct=True)
    df['volatility_rank'] = df.groupby('date')['volatility'].rank(pct=True, ascending=False)
    return df
