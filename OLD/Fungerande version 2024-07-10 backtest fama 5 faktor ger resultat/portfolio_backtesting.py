import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from borsdata_api.constants import DB_FILE_MONTHLY
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import os

# Connect to the SQLite database for monthly data
def connect_db():
    return sqlite3.connect(DB_FILE_MONTHLY)

def calculate_portfolio_returns(df, factor, holding_period='quarterly'):
    df = df.sort_values(by=['date', factor])
    df['rank'] = df.groupby('date', observed=True)[factor].rank(pct=True)
    df['portfolio'] = pd.cut(df['rank'], bins=4, labels=[1, 2, 3, 4])
    
    # Calculate returns for each portfolio
    df['return'] = df.groupby('ins_id', observed=True)['close'].pct_change()
    
    # Correctly adjust for different holding periods
    holding_period_map = {
        'quarterly': 3,
        'yearly': 12,
        '2_years': 24,
        '3_years': 36,
        '5_years': 60
    }

    if holding_period in holding_period_map:
        period_months = holding_period_map[holding_period]
        df['holding_return'] = df.groupby('ins_id', observed=True)['return'].rolling(period_months).apply(lambda x: np.prod(1 + x) - 1).reset_index(level=0, drop=True)
    
    portfolio_returns = df.groupby(['date', 'portfolio'], observed=True)['holding_return'].mean().reset_index()
    return portfolio_returns, df

def calculate_performance_metrics(portfolio_returns):
    metrics = portfolio_returns.groupby('portfolio', observed=True)['holding_return'].agg(['mean', 'std']).reset_index()
    metrics['sharpe'] = metrics['mean'] / metrics['std']
    return metrics

def save_results_to_excel(factor, period, metrics, df_with_portfolio, writer):
    export_dir = r"C:\Users\ander\Documents\Borsdata\Python_Strategi\Exportdata"
    os.makedirs(export_dir, exist_ok=True)
    
    sheet_name = f"{factor}_{period}"
    metrics.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook = writer.book
    worksheet = workbook[sheet_name]
    worksheet['A10'] = "Explanation of Key Metrics and Quartiles:"
    worksheet['A11'] = f"Factor: {factor}"
    worksheet['A12'] = f"Holding Period: {period}"
    worksheet['A13'] = "Quartile 1: Lowest ranked"
    worksheet['A14'] = "Quartile 4: Highest ranked"

    for quantile in metrics['portfolio'].unique():
        subset = df_with_portfolio[df_with_portfolio['portfolio'] == quantile]
        if subset.empty:
            continue

        max_value_factor = subset[factor].max()
        min_value_factor = subset[factor].min()
        median_value_factor = subset[factor].median()

        max_value_rank = subset['rank'].max()
        min_value_rank = subset['rank'].min()
        median_value_rank = subset['rank'].median()

        count = subset.shape[0]
        worksheet[f'A{15 + quantile*5}'] = f"Quartile {quantile} stats:"
        worksheet[f'B{15 + quantile*5}'] = f"Factor Max: {max_value_factor}"
        worksheet[f'C{15 + quantile*5}'] = f"Factor Min: {min_value_factor}"
        worksheet[f'D{15 + quantile*5}'] = f"Factor Median: {median_value_factor}"
        worksheet[f'E{15 + quantile*5}'] = f"Rank Max: {max_value_rank}"
        worksheet[f'F{15 + quantile*5}'] = f"Rank Min: {min_value_rank}"
        worksheet[f'G{15 + quantile*5}'] = f"Rank Median: {median_value_rank}"
        worksheet[f'H{15 + quantile*5}'] = f"Count: {count}"

    # Scatterplot med rank mot utveckling för varje period, färgsatt efter kvartil
    plt.figure(figsize=(10, 6))
    period_df = df_with_portfolio[df_with_portfolio['holding_return'].notna()]
    if period_df.empty:
        print(f"Warning: No data for {factor} in {period}. Skipping plot generation.")
        return
    scatter = plt.scatter(period_df['rank'], period_df['holding_return'], c=period_df['portfolio'], cmap='viridis', alpha=0.5)
    plt.xlabel('Rank')
    plt.ylabel('Return')
    plt.title(f'Scatter Plot of {factor} Rank vs Return for {period}')
    plt.colorbar(scatter, label='Quartile')
    plt_path = os.path.join(export_dir, f"{sheet_name}_rank_vs_return.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A40')

    # Scatterplot med respektive nyckeltal mot utveckling för varje period, färgsatt efter kvartil
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(period_df[factor], period_df['holding_return'], c=period_df['portfolio'], cmap='viridis', alpha=0.5)
    plt.xlabel(factor)
    plt.ylabel('Return')
    plt.title(f'Scatter Plot of {factor} vs Return for {period}')
    plt.colorbar(scatter, label='Quartile')
    plt_path = os.path.join(export_dir, f"{sheet_name}_factor_vs_return.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A60')

    # Boxplot av avkastning för varje kvartil
    plt.figure(figsize=(10, 6))
    period_df.boxplot(column='holding_return', by='portfolio')
    plt.xlabel('Portfolio')
    plt.ylabel('Return')
    plt.title(f'Returns Distribution for Quartiles for {factor} ({period})')
    plt.suptitle('')
    plt_path = os.path.join(export_dir, f"{sheet_name}_quartile_returns.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A80')

    # Bar chart av avkastning för varje kvartil
    plt.figure(figsize=(10, 6))
    quartile_means = period_df.groupby('portfolio', observed=True)['holding_return'].mean()
    quartile_means.plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.xlabel('Portfolio')
    plt.ylabel('Average Return')
    plt.title(f'Average Returns for Quartiles for {factor} ({period})')
    plt_path = os.path.join(export_dir, f"{sheet_name}_quartile_mean_returns.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A100')

def main():
    conn = connect_db()

    # Read factor rankings and price data from the database
    factor_df = pd.read_sql_query("SELECT * FROM factor_rankings", conn)
    price_df = pd.read_sql_query("SELECT ins_id, date, close FROM monthly_price_data", conn)

    # Ensure date is in datetime format
    factor_df['date'] = pd.to_datetime(factor_df['date'])
    price_df['date'] = pd.to_datetime(price_df['date'])

    # Merge factor rankings with price data
    df = pd.merge(factor_df, price_df, on=['ins_id', 'date'], how='left')

    factors = ['size_rank', 'value_rank', 'profitability_rank', 'momentum_rank', 'volatility_rank']

    writer = pd.ExcelWriter(r"C:\Users\ander\Documents\Borsdata\Python_Strategi\Exportdata\portfolio_results.xlsx", engine='openpyxl')

    for factor in factors:
        for period in ['quarterly', 'yearly', '2_years', '3_years', '5_years']:
            print(f"Processing factor {factor} for holding period {period}")
            portfolio_returns, df_with_portfolio = calculate_portfolio_returns(df, factor, holding_period=period)
            if not portfolio_returns.empty:
                metrics = calculate_performance_metrics(portfolio_returns)
                metrics['mean_close'] = df_with_portfolio.groupby('portfolio', observed=True)['close'].mean().values
                save_results_to_excel(factor, period, metrics, df_with_portfolio, writer)

    writer.book.save(r"C:\Users\ander\Documents\Borsdata\Python_Strategi\Exportdata\portfolio_results.xlsx")
    writer.close()
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
