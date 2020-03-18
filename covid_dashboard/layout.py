
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from datetime import datetime, date, time, timedelta
import pandas as pd

# Read CSV
df = pd.read_csv('sg_covid_cases.csv')

# Check the number of days between today and first day
df['date_confirmed_dt'] = df['date_confirmed'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

# Change is_imported to Origin
df['origin'] = df['is_imported'].apply(lambda x: 'Imported' if x is True else 'Local')

max_date = df['date_confirmed_dt'].max()
min_date = df['date_confirmed_dt'].min()
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
    html.Div(id = 'filler'),
    html.Div(id = 'filler2'),
    dcc.Store(id = 'database_subset'),
    html.Button('Print DF', id = 'print_df_button'),
    html.Button('Print DB Subset', id = 'print_database_subset_button'),

    html.Div(
        [html.Div(children = '', id = 'age_range_slider_display'),
        dcc.RangeSlider(
            id = 'age_range_slider',
            min = df['age'].min(),
            max = df['age'].max(),
            step = 1,
            value = [df['age'].min(), df['age'].max()]
        ),
            
        dcc.Checklist(
            id = 'gender_checklist',
            options = [{'label': 'Male', 'value': 'M'},
                        {'label': 'Female', 'value': 'F'}],
            value = ['M', 'F']),
        dcc.Checklist(
            id = 'origin_checklist',
            options = [{'label': 'Imported', 'value': 'Imported'},
                        {'label': 'Local', 'value': 'Local'}],
            value = ['Imported', 'Local']),
        dcc.Dropdown(
            id = 'nationality_dropdown',
            options = [{'label': e, 'value': e} for e in df['nationality'].unique()],
            multi = True,
            value = []
        )
        ]
    ),

    dash_table.DataTable(
        id = 'datatable',
        columns = [{'name': 'No.', 'id': 'case_num'},
                {'name': 'Age', 'id': 'age'},
                {'name': 'Gender', 'id': 'gender'},
                {'name': 'Hospital', 'id': 'hospital'},
                {'name': 'Date Confirmed', 'id': 'date_confirmed'},
                {'name': 'Origin', 'id': 'origin'},
                {'name': 'Nationality', 'id': 'nationality'},
                {'name': 'Residence', 'id': 'residence'},
                {'name': 'Address', 'id': 'residence_address'},
                {'name': 'Places Visited', 'id': 'places_visited'}
                ],
        data = [],
        style_data = {
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_table = {
            'maxHeight': '300px',
            'overflowX': 'scroll'},
        sort_action = 'native',
        hidden_columns = ['residence_latitude', 'residence_longitude', 'date_confirmed_dt']
    ),

    html.Div([
        html.Div(children = datetime.strftime(max_date, '%Y-%m-%d'), id = 'date_slider_display'),
        dcc.Slider(id = 'date_slider', min = 0, max = n_days, step = 1, value = n_days)
    ]),

    html.Div(dcc.Graph(id='map'))

], className="container")

