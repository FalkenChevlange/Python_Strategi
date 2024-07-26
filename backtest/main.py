import sys
import os

# Lägg till projektets rotkatalog till Pythons sökväg
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.drawing.image import Image
from helpers.db_utils import connect_db
from calculate_returns import calculate_portfolio_returns
from calculate_metrics import calculate_performance_metrics
from save_results import save_results_to_excel

def main():
    conn = connect_db()

    factor_df = pd.read_sql_query("SELECT * FROM factor_rankings", conn)
    price_df = pd.read_sql_query("SELECT ins_id, date, close FROM monthly_price_data", conn)

    factor_df['date'] = pd.to_datetime(factor_df['date'])
    price_df['date'] = pd.to_datetime(price_df['date'])

    df = pd.merge(factor_df, price_df, on=['ins_id', 'date'])

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    backup_dir = os.path.join(output_dir, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'portfolio_results.xlsx')

    if os.path.exists(output_file):
        date_str = datetime.now().strftime("%Y-%m-%d")
        version = 1
        while True:
            backup_file = os.path.join(backup_dir, f"portfolio_results_{date_str}_v{version}.xlsx")
            if not os.path.exists(backup_file):
                shutil.copy(output_file, backup_file)
                break
            version += 1

    figures_dir = os.path.join(output_dir, f"figures_{datetime.now().strftime('%Y-%m-%d')}")
    os.makedirs(figures_dir, exist_ok=True)

    writer = pd.ExcelWriter(output_file, engine='openpyxl')

    for factor in ['size_rank', 'value_rank', 'momentum_rank', 'profitability_rank', 'volatility_rank']:
        for period in ['quarterly', 'yearly', '2_years', '3_years', '5_years']:
            print(f"Processing factor {factor} for holding period {period}")
            try:
                portfolio_returns, df_with_portfolio = calculate_portfolio_returns(df, factor, holding_period=period)
            except ValueError as e:
                print(e)
                continue

            if not portfolio_returns.empty:
                metrics = calculate_performance_metrics(portfolio_returns)
                metrics['mean_close'] = df_with_portfolio.groupby('portfolio', observed=True)['close'].mean().values
                save_results_to_excel(factor, period, metrics, df_with_portfolio, writer, figures_dir)

    writer.book.save(output_file)
    writer.close()
    conn.close()

if __name__ == "__main__":
    main()
