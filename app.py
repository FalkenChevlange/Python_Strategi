import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Anslut till SQLite-databasen
db_path = r'C:\Users\ander\Documents\Borsdata\Python_Strategi\Exportdata\borsdata_monthly.db'
engine = create_engine(f'sqlite:///{db_path}')

# Hämta data från tabellen 'factor_rankings'
query = "SELECT * FROM factor_rankings"
df = pd.read_sql(query, engine)

# Kontrollera startdatum
df['date'] = pd.to_datetime(df['date'])
start_year = df['date'].min().year
print("Tidigt datum i datasetet:", df['date'].min())

# Lägg till kvartilkolumn
df['quartile'] = pd.qcut(df['momentum_rank'], 4, labels=False) + 1

# Beräkna procentuell förändring efter 3, 6, 9 månader, 1, 2, 3 och 5 år
df = df.sort_values(by=['ins_id', 'date'])
df['return_3m'] = df.groupby('ins_id')['close'].pct_change(periods=3) * 100
df['return_6m'] = df.groupby('ins_id')['close'].pct_change(periods=6) * 100
df['return_9m'] = df.groupby('ins_id')['close'].pct_change(periods=9) * 100
df['return_1y'] = df.groupby('ins_id')['close'].pct_change(periods=12) * 100
df['return_2y'] = df.groupby('ins_id')['close'].pct_change(periods=24) * 100
df['return_3y'] = df.groupby('ins_id')['close'].pct_change(periods=36) * 100
df['return_5y'] = df.groupby('ins_id')['close'].pct_change(periods=60) * 100

# Filtrera bort data som inte har tillräckligt med historik
df = df[df['date'] >= pd.Timestamp(f"{start_year + 5}-01-01")]

# Skapa en kolumn som representerar "dagar sedan inköpsdag"
df['days_since_purchase'] = df.groupby('ins_id')['date'].transform(lambda x: (x - x.min()).dt.days)

# Funktion för att ta bort outliers
def remove_outliers(data, column, threshold=1.5):
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

# Skapa en Dash-applikation
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Börsdata - Faktoranalys"),
    dcc.Dropdown(
        id='factor-dropdown',
        options=[
            {'label': 'Momentum', 'value': 'momentum_rank'},
            {'label': 'Value', 'value': 'value_factor_rank'},
            {'label': 'Profitability', 'value': 'profitability_rank'},
            {'label': 'Volatility', 'value': 'volatility_rank'},
            {'label': 'Size', 'value': 'size_rank'}
        ],
        value='momentum_rank'
    ),
    dcc.Dropdown(
        id='scatterplot-type-dropdown',
        options=[
            {'label': 'Rank', 'value': 'rank'},
            {'label': 'Value', 'value': 'value'}
        ],
        value='rank'
    ),
    dcc.Tabs([
        dcc.Tab(label='Boxplot', children=[
            dcc.Graph(id='boxplot-graph'),
            html.Label("Välj tidshorisont:"),
            dcc.RadioItems(
                id='boxplot-horizon',
                options=[
                    {'label': '3 månader', 'value': 'return_3m'},
                    {'label': '6 månader', 'value': 'return_6m'},
                    {'label': '9 månader', 'value': 'return_9m'},
                    {'label': '1 år', 'value': 'return_1y'},
                    {'label': '2 år', 'value': 'return_2y'},
                    {'label': '3 år', 'value': 'return_3y'},
                    {'label': '5 år', 'value': 'return_5y'}
                ],
                value='return_1y'
            ),
            html.Label("Visa outliers:"),
            dcc.RadioItems(
                id='boxplot-outliers',
                options=[
                    {'label': 'Ja', 'value': 'all'},
                    {'label': 'Nej', 'value': 'outliers'}
                ],
                value='all'
            ),
            html.Label("Exkludera extrema värden:"),
            dcc.RadioItems(
                id='exclude-extremes',
                options=[
                    {'label': 'Ja', 'value': 'yes'},
                    {'label': 'Nej', 'value': 'no'}
                ],
                value='no'
            ),
            html.Div(id='boxplot-nyckeltal')
        ]),
        dcc.Tab(label='Violinchart', children=[
            dcc.Graph(id='violin-graph'),
            html.Label("Välj tidshorisont:"),
            dcc.RadioItems(
                id='violin-horizon',
                options=[
                    {'label': '3 månader', 'value': 'return_3m'},
                    {'label': '6 månader', 'value': 'return_6m'},
                    {'label': '9 månader', 'value': 'return_9m'},
                    {'label': '1 år', 'value': 'return_1y'},
                    {'label': '2 år', 'value': 'return_2y'},
                    {'label': '3 år', 'value': 'return_3y'},
                    {'label': '5 år', 'value': 'return_5y'}
                ],
                value='return_1y'
            ),
            html.Label("Exkludera extrema värden:"),
            dcc.RadioItems(
                id='exclude-extremes-violin',
                options=[
                    {'label': 'Ja', 'value': 'yes'},
                    {'label': 'Nej', 'value': 'no'}
                ],
                value='no'
            ),
            html.Div(id='violin-nyckeltal')
        ]),
        dcc.Tab(label='Scatterplot', children=[
            dcc.Graph(id='scatterplot-graph'),
            html.Label("Välj tidshorisont:"),
            dcc.RadioItems(
                id='scatterplot-horizon',
                options=[
                    {'label': '3 månader', 'value': 'return_3m'},
                    {'label': '6 månader', 'value': 'return_6m'},
                    {'label': '9 månader', 'value': 'return_9m'},
                    {'label': '1 år', 'value': 'return_1y'},
                    {'label': '2 år', 'value': 'return_2y'},
                    {'label': '3 år', 'value': 'return_3y'},
                    {'label': '5 år', 'value': 'return_5y'}
                ],
                value='return_1y'
            ),
            html.Label("Exkludera extrema värden:"),
            dcc.RadioItems(
                id='exclude-extremes-scatter',
                options=[
                    {'label': 'Ja', 'value': 'yes'},
                    {'label': 'Nej', 'value': 'no'}
                ],
                value='no'
            ),
            html.Div(id='scatterplot-nyckeltal')
        ]),
        dcc.Tab(label='Graf Utveckling', children=[
            dcc.Graph(id='line-graph'),
            html.Label("Välj tidshorisont:"),
            dcc.RadioItems(
                id='line-horizon',
                options=[
                    {'label': '3 månader', 'value': '3m'},
                    {'label': '6 månader', 'value': '6m'},
                    {'label': '9 månader', 'value': '9m'},
                    {'label': '1 år', 'value': '1y'},
                    {'label': '2 år', 'value': '2y'},
                    {'label': '3 år', 'value': '3y'},
                    {'label': '5 år', 'value': '5y'}
                ],
                value='1y'
            ),
            html.Div(id='line-nyckeltal')
        ])
    ])
])

# Callback-funktioner för att uppdatera graferna baserat på valda faktorn

@app.callback(
    [Output('boxplot-graph', 'figure'),
     Output('boxplot-nyckeltal', 'children')],
    [Input('boxplot-horizon', 'value'),
     Input('boxplot-outliers', 'value'),
     Input('factor-dropdown', 'value'),
     Input('exclude-extremes', 'value')]
)
def update_boxplot(horizon, outliers, factor, exclude_extremes):
    filtered_data = df.copy()
    if exclude_extremes == 'yes':
        filtered_data = remove_outliers(filtered_data, horizon)
    filtered_data['quartile'] = pd.qcut(filtered_data[factor], 4, labels=False) + 1
    fig = px.box(filtered_data, x='quartile', y=horizon, points=outliers)
    fig.update_layout(yaxis_title='Procentuell Förändring (%)')
    
    # Beräkna nyckeltal
    nyckeltal = []
    for quartile in range(1, 5):
        quartile_data = filtered_data[filtered_data['quartile'] == quartile]
        num_obs = len(quartile_data)
        median_all = filtered_data[horizon].median()
        num_above_median = len(quartile_data[quartile_data[horizon] > median_all])
        pct_above_median = num_above_median / num_obs * 100 if num_obs > 0 else 0
        nyckeltal.append(html.Div([
            html.H4(f'Kvartil {quartile}'),
            html.P(f'Antal observationer: {num_obs}'),
            html.P(f'Andel över medianen: {pct_above_median:.2f}%')
        ]))
    
    return fig, nyckeltal

@app.callback(
    [Output('violin-graph', 'figure'),
     Output('violin-nyckeltal', 'children')],
    [Input('violin-horizon', 'value'),
     Input('factor-dropdown', 'value'),
     Input('exclude-extremes-violin', 'value')]
)
def update_violin(horizon, factor, exclude_extremes):
    filtered_data = df.copy()
    if exclude_extremes == 'yes':
        filtered_data = remove_outliers(filtered_data, horizon)
    filtered_data['quartile'] = pd.qcut(filtered_data[factor], 4, labels=False) + 1
    
    fig = go.Figure()
    
    for quartile in range(1, 5):
        quartile_data = filtered_data[filtered_data['quartile'] == quartile]
        fig.add_trace(go.Violin(
            x=quartile_data['quartile'],
            y=quartile_data[horizon],
            name=f'Kvartil {quartile}',
            box_visible=True,
            points='all'
        ))
    
    fig.update_layout(
        yaxis_title='Procentuell Förändring (%)',
        violinmode='group'
    )
    
    # Beräkna nyckeltal
    nyckeltal = []
    for quartile in range(1, 5):
        quartile_data = filtered_data[filtered_data['quartile'] == quartile]
        num_obs = len(quartile_data)
        median_all = filtered_data[horizon].median()
        num_above_median = len(quartile_data[quartile_data[horizon] > median_all])
        pct_above_median = num_above_median / num_obs * 100 if num_obs > 0 else 0
        nyckeltal.append(html.Div([
            html.H4(f'Kvartil {quartile}'),
            html.P(f'Antal observationer: {num_obs}'),
            html.P(f'Andel över medianen: {pct_above_median:.2f}%')
        ]))
    
    return fig, nyckeltal

@app.callback(
    [Output('scatterplot-graph', 'figure'),
     Output('scatterplot-nyckeltal', 'children')],
    [Input('scatterplot-horizon', 'value'),
     Input('factor-dropdown', 'value'),
     Input('scatterplot-type-dropdown', 'value'),
     Input('exclude-extremes-scatter', 'value')]
)
def update_scatterplot(horizon, factor, scatter_type, exclude_extremes):
    filtered_data = df.copy()
    if exclude_extremes == 'yes':
        filtered_data = remove_outliers(filtered_data, horizon)
    filtered_data['quartile'] = pd.qcut(filtered_data[factor], 4, labels=False) + 1
    
    if scatter_type == 'rank':
        fig = px.scatter(filtered_data, x=factor, y=horizon, color='quartile', trendline='ols')
    else:
        factor_value_col = factor.replace('rank', 'value')  # Assuming the value columns are named similarly
        fig = px.scatter(filtered_data, x=factor_value_col, y=horizon, color='quartile', trendline='ols')
    
    fig.update_layout(yaxis_title='Procentuell Förändring (%)')
    
    # Beräkna nyckeltal
    nyckeltal = []
    for quartile in range(1, 5):
        quartile_data = filtered_data[filtered_data['quartile'] == quartile]
        num_obs = len(quartile_data)
        median_all = filtered_data[horizon].median()
        num_above_median = len(quartile_data[quartile_data[horizon] > median_all])
        pct_above_median = num_above_median / num_obs * 100 if num_obs > 0 else 0
        nyckeltal.append(html.Div([
            html.H4(f'Kvartil {quartile}'),
            html.P(f'Antal observationer: {num_obs}'),
            html.P(f'Andel över medianen: {pct_above_median:.2f}%')
        ]))
    
    return fig, nyckeltal

@app.callback(
    [Output('line-graph', 'figure'),
     Output('line-nyckeltal', 'children')],
    [Input('line-horizon', 'value'),
     Input('factor-dropdown', 'value')]
)
def update_line(horizon, factor):
    filtered_data = df.copy()
    filtered_data['quartile'] = pd.qcut(filtered_data[factor], 4, labels=False) + 1
    
    # Begränsa data till max 5 års utveckling
    max_days = 5 * 365  # 5 år i dagar
    filtered_data = filtered_data[filtered_data['days_since_purchase'] <= max_days]
    
    # Beräkna medianutveckling för varje dag sedan inköpsdag
    numeric_columns = filtered_data.select_dtypes(include=['number']).columns
    grouped_data = filtered_data.groupby(['days_since_purchase', 'quartile'])[numeric_columns].median()
    grouped_data = grouped_data.reset_index(drop=False)  # Återställ index utan att duplicera 'quartile'

    # Filtrera baserat på vald horisont
    horizon_mapping = {
        '3m': 90,
        '6m': 180,
        '9m': 270,
        '1y': 365,
        '2y': 2 * 365,
        '3y': 3 * 365,
        '5y': 5 * 365
    }
    horizon_days = horizon_mapping[horizon]
    grouped_data = grouped_data[grouped_data['days_since_purchase'] <= horizon_days]
    
    fig = px.line(grouped_data, x='days_since_purchase', y='close', color='quartile')
    fig.update_layout(yaxis_title='Procentuell Förändring (%)', xaxis_title='Dagar sedan inköpsdag')
    
    # Beräkna nyckeltal
    nyckeltal = []
    for quartile in range(1, 5):
        quartile_data = filtered_data[filtered_data['quartile'] == quartile]
        num_obs = len(quartile_data)
        median_all = filtered_data['close'].median()
        num_above_median = len(quartile_data[quartile_data['close'] > median_all])
        pct_above_median = num_above_median / num_obs * 100 if num_obs > 0 else 0
        nyckeltal.append(html.Div([
            html.H4(f'Kvartil {quartile}'),
            html.P(f'Antal observationer: {num_obs}'),
            html.P(f'Andel över medianen: {pct_above_median:.2f}%')
        ]))
    
    return fig, nyckeltal


if __name__ == '__main__':
    app.run_server(debug=True)
