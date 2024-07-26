import pandas as pd
import numpy as np
import statsmodels.api as sm

def add_regression_to_plot(ax, x, y):
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
