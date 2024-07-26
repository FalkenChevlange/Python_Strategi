def calculate_performance_metrics(portfolio_returns):
    metrics = portfolio_returns.groupby('portfolio', observed=True)['holding_return'].agg(['mean', 'std']).reset_index()
    metrics['sharpe'] = metrics['mean'] / metrics['std']
    return metrics
