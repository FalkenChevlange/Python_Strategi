import sys
import os
import pandas as pd 

# Lägg till projektets rotkatalog till Pythons sökväg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.db_utils import connect_db
from calculate_factors import calculate_rolling_factors, calculate_factors
from rank_factors import rank_factors
from save_rankings import save_rankings

def main():
    conn = connect_db()
    print("Reading monthly_price_data...")
    price_df = pd.read_sql_query("SELECT * FROM monthly_price_data", conn)
    print("Reading monthly_report_data...")
    report_df = pd.read_sql_query("SELECT * FROM monthly_report_data", conn)
    
    print("Calculating rolling factors...")
    rolling_report_df = calculate_rolling_factors(report_df)
    print("Calculating factors...")
    factors_df = calculate_factors(price_df, rolling_report_df)
    print("Ranking factors...")
    ranked_df = rank_factors(factors_df)
    
    print("Saving rankings to database...")
    save_rankings(ranked_df)
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
