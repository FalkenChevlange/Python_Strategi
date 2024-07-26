import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import openpyxl
from openpyxl.drawing.image import Image
from helpers.plotting_utils import add_regression_to_plot

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
