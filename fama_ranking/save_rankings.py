import sqlite3
from helpers.db_utils import connect_db

def save_rankings_to_db(df):
    conn = connect_db()
    print("Saving to SQL...")
    df.to_sql('factor_rankings', conn, if_exists='replace', index=False)
    print("Data saved to SQL.")
    conn.close()

def save_rankings(df):
    # Justera för att inkludera 'value_factor_rank' istället för 'value_rank'
    ranking_df = df[['ins_id', 'date', 'size_rank', 'value_factor_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']]
    print("Saving adjusted rankings...")
    save_rankings_to_db(ranking_df)
