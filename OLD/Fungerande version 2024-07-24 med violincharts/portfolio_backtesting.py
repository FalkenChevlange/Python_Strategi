import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from borsdata_api.constants import DB_FILE_MONTHLY
import openpyxl
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import os
import statsmodels.api as sm
import shutil
from datetime import datetime

# Connect to the SQLite database for monthly data
def connect_db():
    return sqlite3.connect(DB_FILE_MONTHLY)

def calculate_portfolio_returns(df, factor, holding_period='quarterly'):
    if factor not in df.columns:
        raise ValueError(f"Factor '{factor}' not found in DataFrame columns")
        
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

def add_regression_to_plot(ax, x, y):
    # Drop NaN and inf values and align indices
    df = pd.DataFrame({'x': x, 'y': y}).dropna().replace([np.inf, -np.inf], np.nan).dropna()
    x_clean = df['x']
    y_clean = df['y']

    x_with_const = sm.add_constant(x_clean)
    model = sm.OLS(y_clean, x_with_const).fit()
    intercept, slope = model.params
    r_squared = model.rsquared

    regression_label = f'R² = {r_squared:.2f}\nSlope = {slope:.2f}\nIntercept = {intercept:.2f}'
    ax.plot(x_clean, intercept + slope * x_clean, label=regression_label, color='red')
    ax.legend()

def save_results_to_excel(factor, period, metrics, df_with_portfolio, writer, export_dir):
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

    # Scatterplot med rank mot utveckling för varje period, färgsatt efter kvartil och med regression
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
    add_regression_to_plot(plt.gca(), period_df['rank'], period_df['holding_return'])
    plt_path = os.path.join(export_dir, f"{sheet_name}_rank_vs_return.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A40')

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
    worksheet.add_image(img, 'A70')

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

    # Violin plot av avkastning för varje kvartil
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='portfolio', y='holding_return', hue='portfolio', data=period_df, palette='viridis', legend=False)
    plt.axhline(period_df['holding_return'].mean(), color='red', linestyle='--', label='Mean')
    plt.axhline(period_df['holding_return'].median(), color='blue', linestyle='--', label='Median')
    plt.xlabel('Portfolio')
    plt.ylabel('Return')
    plt.title(f'Violin Plot of Returns Distribution for Quartiles for {factor} ({period})')
    plt.legend()
    plt_path = os.path.join(export_dir, f"{sheet_name}_quartile_violin_returns.png")
    plt.savefig(plt_path)
    plt.close()

    img = openpyxl.drawing.image.Image(plt_path)
    worksheet.add_image(img, 'A130')

    # Beräkna och lägg till antal observationer över medel eller median
    overall_mean = period_df['holding_return'].mean()
    overall_median = period_df['holding_return'].median()

    obs_above_mean = period_df.groupby('portfolio', observed=True)['holding_return'].apply(lambda x: (x > overall_mean).sum())
    obs_above_median = period_df.groupby('portfolio', observed=True)['holding_return'].apply(lambda x: (x > overall_median).sum())

    worksheet['A150'] = "Number of observations above mean:"
    for i, (portfolio, count) in enumerate(obs_above_mean.items()):
        worksheet[f'A{151 + i}'] = f"Quartile {portfolio}: {count}"

    worksheet['A160'] = "Number of observations above median:"
    for i, (portfolio, count) in enumerate(obs_above_median.items()):
        worksheet[f'A{161 + i}'] = f"Quartile {portfolio}: {count}"

def main():
    conn = connect_db()

    # Read factor rankings and price data from the database
    factor_df = pd.read_sql_query("SELECT * FROM factor_rankings", conn)
    price_df = pd.read_sql_query("SELECT ins_id, date, close FROM monthly_price_data", conn)

    # Ensure date is in datetime format
    factor_df['date'] = pd.to_datetime(factor_df['date'])
    price_df['date'] = pd.to_datetime(price_df['date'])

    # Merge factor rankings with price data
    df = pd.merge(factor_df, price_df, on=['ins_id', 'date'])

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    backup_dir = os.path.join(output_dir, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'portfolio_results.xlsx')

    # Check if the Excel file already exists and create a backup if it does
    if os.path.exists(output_file):
        date_str = datetime.now().strftime("%Y-%m-%d")
        version = 1
        while True:
            backup_file = os.path.join(backup_dir, f"portfolio_results_{date_str}_v{version}.xlsx")
            if not os.path.exists(backup_file):
                shutil.copy(output_file, backup_file)
                break
            version += 1

    # Create a new directory for figures with today's date
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
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")

