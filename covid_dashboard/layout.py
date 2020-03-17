
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime, date, time
import pandas as pd

# Read CSV
df = pd.read_csv('sg_covid_cases.csv')



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

    html.Div(dcc.Graph(id='map'))

], className="container")

