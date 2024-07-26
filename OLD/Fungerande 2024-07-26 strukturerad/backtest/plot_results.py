import matplotlib.pyplot as plt
import seaborn as sns
from helpers.plotting_utils import add_regression_to_plot

def plot_results(df_with_portfolio, factor, period, export_dir):
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
    plt_path = os.path.join(export_dir, f"{factor}_{period}_rank_vs_return.png")
    plt.savefig(plt_path)
    plt.close()
