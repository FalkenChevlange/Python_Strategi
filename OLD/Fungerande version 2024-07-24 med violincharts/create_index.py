import pandas as pd
import numpy as np
import sqlite3
from borsdata_api.constants import DB_FILE

# Connect to the SQLite database
def connect_db():
    return sqlite3.connect(DB_FILE)

def create_price_weighted_index(conn):
    price_df = pd.read_sql_query("SELECT * FROM price_data", conn)
    price_df['date'] = pd.to_datetime(price_df['date'])
    grouped_df = price_df.groupby('date').agg({'close': 'sum', 'ins_id': 'count'}).reset_index()
    grouped_df['price_weighted_index'] = grouped_df['close'] / grouped_df['ins_id']
    return grouped_df[['date', 'price_weighted_index']]

def create_market_cap_weighted_index(conn):
    price_df = pd.read_sql_query("SELECT * FROM price_data", conn)
    report_df = pd.read_sql_query("SELECT ins_id, report_start_date, number_of_shares FROM report_data", conn)
    
    price_df['date'] = pd.to_datetime(price_df['date'])
    report_df['report_start_date'] = pd.to_datetime(report_df['report_start_date'])
    
    report_df = report_df.drop_duplicates(subset=['ins_id', 'report_start_date']).sort_values(by='report_start_date')
    combined_df = pd.merge_asof(price_df.sort_values('date'), report_df.sort_values('report_start_date'), by='ins_id', left_on='date', right_on='report_start_date')
    
    combined_df = combined_df.groupby('ins_id', group_keys=False).apply(lambda x: x.set_index('date').ffill().bfill().reset_index())
    
    combined_df['market_cap'] = combined_df['close'] * combined_df['number_of_shares']
    combined_df['weighted_close'] = combined_df['close'] * combined_df['market_cap']
    
    grouped_df = combined_df.groupby('date').agg({'weighted_close': 'sum', 'market_cap': 'sum'}).reset_index()
    grouped_df['market_cap_weighted_index'] = grouped_df['weighted_close'] / grouped_df['market_cap']
    
    return grouped_df[['date', 'market_cap_weighted_index']]

def create_equal_weighted_index(conn):
    price_df = pd.read_sql_query("SELECT * FROM price_data", conn)
    price_df['date'] = pd.to_datetime(price_df['date'])
    grouped_df = price_df.groupby('date').agg({'close': 'mean'}).reset_index()
    grouped_df.rename(columns={'close': 'equal_weighted_index'}, inplace=True)
    return grouped_df[['date', 'equal_weighted_index']]

def calculate_risk_parity_weights(cov_matrix):
    inv_vol = 1 / np.sqrt(np.diag(cov_matrix))
    inv_vol /= inv_vol.sum()
    return inv_vol

def create_risk_parity_index(conn, lookback_period=252):
    price_df = pd.read_sql_query("SELECT * FROM price_data", conn)
    price_df['date'] = pd.to_datetime(price_df['date'])
    price_pivot = price_df.pivot(index='date', columns='ins_id', values='close')
    
    # Calculate rolling returns and covariance matrix
    rolling_cov_matrices = price_pivot.pct_change().rolling(window=lookback_period).cov(pairwise=True)
    
    risk_parity_indices = []
    
    for date in rolling_cov_matrices.index.levels[0]:
        cov_matrix = rolling_cov_matrices.loc[date]
        if not cov_matrix.empty:
            weights = calculate_risk_parity_weights(cov_matrix)
            returns = price_pivot.pct_change().loc[date]
            risk_parity_index = np.dot(weights, returns)
            risk_parity_indices.append({'date': date, 'risk_parity_index': risk_parity_index})
    
    risk_parity_df = pd.DataFrame(risk_parity_indices)
    return risk_parity_df

def save_indices_to_db(conn):
    price_weighted_df = create_price_weighted_index(conn)
    market_cap_weighted_df = create_market_cap_weighted_index(conn)
    equal_weighted_df = create_equal_weighted_index(conn)
    risk_parity_df = create_risk_parity_index(conn)
    
    merged_df = price_weighted_df.merge(market_cap_weighted_df, on='date', how='outer')
    merged_df = merged_df.merge(equal_weighted_df, on='date', how='outer')
    merged_df = merged_df.merge(risk_parity_df, on='date', how='outer')
    
    merged_df.to_sql('index_data', conn, if_exists='replace', index=False)
    print("All index data saved to database.")

if __name__ == "__main__":
    conn = connect_db()
    save_indices_to_db(conn)
    conn.close()
    print("All index creation completed.")
