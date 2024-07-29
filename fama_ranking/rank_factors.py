import pandas as pd

def custom_rank(series):
    """
    Rankar värden i en serie där negativa värden rankas högst.
    
    Parametrar:
    series (Series): Pandas Series att ranka.
    
    Returnerar:
    Series: Normaliserad rankning mellan 0 och 1.
    """
    print("Utför specialrankning...")
    
    positive_values = series[series > 0].rank(method='min', ascending=True)
    negative_values = series[series <= 0].rank(method='min', ascending=False)
    
    combined_rank = pd.concat([positive_values, negative_values]).fillna(len(series) + 1)
    normalized_rank = (combined_rank - combined_rank.min()) / (combined_rank.max() - combined_rank.min())
    
    print("Specialrankning klar.")
    return normalized_rank

def rank_factors(df):
    """
    Rankar olika finansiella faktorer i en DataFrame.
    
    Parametrar:
    df (DataFrame): DataFrame innehållande finansiella faktorer.
    
    Returnerar:
    DataFrame: DataFrame med rankade faktorer.
    """
    print("Rankar faktorer...")
    
    df['size_rank'] = df.groupby('date')['market_cap'].rank(pct=True)
    df['value_factor_rank'] = df.groupby('date')['value_factor'].transform(custom_rank)
    df['profitability_rank'] = df.groupby('date')['profitability'].rank(pct=True)
    df['momentum_rank'] = df.groupby('date')['momentum'].rank(pct=True)
    df['volatility_rank'] = df.groupby('date')['volatility'].rank(pct=True, ascending=False)
    
    print("Faktorer rankade.")
    return df
