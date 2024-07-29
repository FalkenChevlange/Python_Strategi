import sqlite3
from borsdata_api.constants import DB_FILE_MONTHLY

def save_rankings_to_db(df):
    """
    Sparar rankad data till en SQLite-databas.
    
    Parametrar:
    df (DataFrame): DataFrame innehållande rankad data.
    """
    print("Sparar rankningar i databasen...")
    
    conn = sqlite3.connect(DB_FILE_MONTHLY)
    df.to_sql('factor_rankings', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Rankningar sparade i databasen.")

def save_rankings(df):
    """
    Förbereder data för lagring genom att inkludera relevanta rankningskolumner.
    
    Parametrar:
    df (DataFrame): DataFrame innehållande rankad data.
    """
    print("Förbereder rankningar för databasen...")
    
    ranking_df = df[['ins_id', 'date', 'size_rank', 'value_factor_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']]
    save_rankings_to_db(ranking_df)
    
    print("Rankningar förberedda och sparade.")
