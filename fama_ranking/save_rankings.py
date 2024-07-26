import pandas as pd
from helpers.db_utils import connect_db

def save_rankings_to_db(df):
    conn = connect_db()
    ranking_df = df[['ins_id', 'date', 'size_rank', 'value_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']]
    ranking_df.to_sql('factor_rankings', conn, if_exists='replace', index=False)
    conn.close()
    print("Factor rankings saved to database.")
