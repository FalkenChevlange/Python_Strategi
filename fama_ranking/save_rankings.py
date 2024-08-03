import sqlite3
import pandas as pd
from borsdata_api.constants import DB_FILE_MONTHLY

def save_rankings_to_db(df):
    """
    Sparar rankade faktorer och ursprungliga värden i databasen.
    
    Parametrar:
    df (DataFrame): DataFrame innehållande rankade faktorer och ursprungliga värden.
    """
    conn = sqlite3.connect(DB_FILE_MONTHLY)
    df.to_sql('factor_rankings', conn, if_exists='replace', index=False)
    conn.close()

def save_rankings(df):
    """
    Förbereder data för att sparas i databasen genom att välja nödvändiga kolumner.
    
    Parametrar:
    df (DataFrame): DataFrame innehållande rankade faktorer och ursprungliga värden.
    """
    # Välj nödvändiga kolumner
    ranking_df = df[['ins_id', 'date', 'close', 'revenues', 'gross_income', 'operating_income', 
                     'earnings_per_share', 'number_of_shares', 'market_cap', 'operating_earnings_per_share', 
                     'value_factor', 'profitability', 'momentum', 'volatility', 
                     'size_rank', 'market_cap_value', 'value_factor_rank', 'value_factor_value', 
                     'profitability_rank', 'profitability_value', 'momentum_rank', 'momentum_value', 
                     'volatility_rank', 'volatility_value']]
    
    # Lägg till alla kolumner från rapportdata och prisdata som inte redan är inkluderade
    additional_columns = [col for col in df.columns if col not in ranking_df.columns]
    ranking_df = pd.concat([ranking_df, df[additional_columns]], axis=1)
    
    save_rankings_to_db(ranking_df)
