import sys
import os
import pandas as pd 

# Lägg till projektets rotkatalog till Pythons sökväg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.db_utils import connect_db
from calculate_factors import calculate_rolling_factors, calculate_factors
from rank_factors import rank_factors
from save_rankings import save_rankings_to_db

def main():
    conn = connect_db()
    price_df = pd.read_sql_query("SELECT * FROM monthly_price_data", conn)
    report_df = pd.read_sql_query("SELECT * FROM monthly_report_data", conn)
    rolling_report_df = calculate_rolling_factors(report_df)
    factors_df = calculate_factors(price_df, rolling_report_df)
    ranked_df = rank_factors(factors_df)
    save_rankings_to_db(ranked_df)
    conn.close()

if __name__ == "__main__":
    main()
