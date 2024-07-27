import sqlite3

def save_rankings_to_db(df):
    conn = sqlite3.connect('path_to_your_database.db')
    df.to_sql('rankings', conn, if_exists='replace', index=False)
    conn.close()

def save_rankings(df):
    # Justera för att inkludera 'value_factor_rank' istället för 'value_rank'
    ranking_df = df[['ins_id', 'date', 'size_rank', 'value_factor_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']]
    save_rankings_to_db(ranking_df)
