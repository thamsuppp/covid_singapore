
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime, date, time, timedelta
import pandas as pd

# Read CSV
df = pd.read_csv('sg_covid_cases.csv')

# Check the number of days between today and first day
df['date_confirmed'] = df['date_confirmed'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

max_date = df['date_confirmed'].max()
min_date = df['date_confirmed'].min()
n_days = (max_date - min_date).days + 1


### Dash app layout
layout = html.Div([
    html.Div([html.H1("Singapore COVID-19 Cases")],
             style={'textAlign': "center", "padding-bottom": "10", "padding-top": "10"}),
    html.Div([
        dcc.Input(id = 'input', placeholder = 'Search...'),
        html.Button('Search', id = 'search_button'),
        html.Div(children = 'Singapore', id = 'output'),
        dcc.Store(id = 'database')
    ]),


    dash_table.DataTable(
        id = 'datatable',
        columns = [{'name': i, 'id': i} for i in df.columns],
        data = df.to_dict('records'),
        style_data = {
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_table = {
            'maxHeight': '300px',
            'overflowX': 'scroll'},
        sort_action = 'native',
        row_selectable = 'multi',
        selected_rows = [i for i in range(0, len(df))],
        hidden_columns = ['residence_latitude', 'residence_longitude']
    ),

    html.Div([
        html.Div(children = max_date, id = 'date_slider_display'),
        dcc.Slider(id = 'date_slider', min = 0, max = n_days, step = 1, value = n_days)
    ]),

    html.Div(dcc.Graph(id='map'))

], className="container")

