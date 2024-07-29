import sys
import os
import pandas as pd 

# Lägg till projektets rotkatalog till Pythons sökväg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.db_utils import connect_db
from calculate_factors import calculate_rolling_factors, calculate_factors
from rank_factors import rank_factors
from save_rankings import save_rankings
from borsdata_api.constants import DB_FILE_MONTHLY

def main():
    """
    Huvudfunktionen för att läsa data, beräkna faktorer, ranka dem och spara resultatet i databasen.
    """
    conn = connect_db()
    print("Läser in prisdata...")
    price_df = pd.read_sql_query("SELECT * FROM monthly_price_data", conn)
    print("Läser in rapportdata...")
    report_df = pd.read_sql_query("SELECT * FROM monthly_report_data", conn)
    
    print("Beräknar rullande faktorer...")
    rolling_report_df = calculate_rolling_factors(report_df)
    print("Beräknar faktorer...")
    factors_df = calculate_factors(price_df, rolling_report_df)
    print("Rankar faktorer...")
    ranked_df = rank_factors(factors_df)
    
    print("Sparar rankningar i databasen...")
    save_rankings(ranked_df)
    conn.close()
    print("Klar.")

if __name__ == "__main__":
    main()
