
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
from datetime import datetime, date, time, timedelta
import pandas as pd
import sqlalchemy

# Connect to database

# #Using App Engine
# engine = sqlalchemy.create_engine(
#     # Equivalent URL:
#     # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
#     sqlalchemy.engine.url.URL(
#         drivername="mysql+pymysql",
#         username='root',
#         password='isaactham',
#         database='covid_sg_data',
#         query={"unix_socket": "/cloudsql/{}".format('covidsg:us-east1:covidsgdatabase')},
#     ),
#     # ... Specify additional properties here.
#     # ...
# )

# Locally
#engine = sqlalchemy.create_engine('mysql+pymysql://root:isaactham@127.0.0.1/covid_sg_data')
#connection = engine.connect()

# Read Cases
#df = pd.read_sql_query('SELECT * FROM cases', connection)
df = pd.read_csv('sg_covid_cases.csv')

df['is_imported'] = df['is_imported'].apply(lambda x: True if x == 1 else False)
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

    html.H3('As of {} there are {} confirmed cases in Singapore.'.format(
        datetime.strftime(df['date_confirmed_dt'].max(), '%d %b'),len(df), sum(df['date_confirmed_dt'] == df['date_confirmed_dt'].max()))),
    
    dcc.Store(id = 'database'),
    html.Div(id = 'filler'),
    html.Div(id = 'filler2'),
    dcc.Store(id = 'database_subset'),
    # html.Button('Print DF', id = 'print_df_button'),
    # html.Button('Print DB Subset', id = 'print_database_subset_button'),

    html.Div(
        [

        html.Div([

        html.Div([
        html.Div(children = '', id = 'age_range_slider_display'),
        dcc.RangeSlider(
            id = 'age_range_slider',
            min = df['age'].min(),
            max = df['age'].max(),
            step = 1,
            value = [df['age'].min(), df['age'].max()]
        )], style = dict(
            width = '40%',
            verticalAlign = 'middle',
            display = 'table-cell'
        ))
        ,
        
        html.Div([    
        dcc.Checklist(
            id = 'gender_checklist',
            options = [{'label': 'Male', 'value': 'M'},
                        {'label': 'Female', 'value': 'F'}],
            value = ['M', 'F'])
            ], style = dict(
            width = '10%',
            verticalAlign = 'middle',
            display = 'table-cell'
        )),
        
        html.Div([
        dcc.Checklist(
            id = 'origin_checklist',
            options = [{'label': 'Imported', 'value': 'Imported'},
                        {'label': 'Local', 'value': 'Local'}],
            value = ['Imported', 'Local'])
            ], style = dict(
            width = '10%',
            verticalAlign = 'middle',
            display = 'table-cell'
            )),

        html.Div([
        dcc.Checklist(
            id = 'select_all_nationality_checklist',
            options =[{'label': 'All Nationalities', 'value': 'All'}],
            value = ['All'])
            ], style = dict(
            width = '8%',
            verticalAlign = 'middle',
            display = 'table-cell'
            )),


        html.Div(
        [
            html.A(
                "Download",
                id="download-link",
                download="data.csv",
                href="#",
                className="btn btn-primary",
                target="_blank",
                style=dict(height='30px', width = '100px', verticalAlign = 'middle')
            )
        ],
        style=dict(
            height='2px',
            width='8%',
            display='table-cell',
            verticalAlign="middle",
        )),

        html.Div(
        [
            html.Button(
                "Info",
                id="info_button",
                className="btn btn-primary",
                style=dict(height='30px', width = '80px', verticalAlign = 'middle')
            ),

            dbc.Modal(
            [
                dbc.ModalHeader("Info"),
                dbc.ModalBody('''The data on Singapore COVID-19 cases has been obtained from the Ministry of Health's website. The data is updated daily when MOH releases new case data.
 
                The patients can be filtered according to age, gender, imported/local and nationality with the filters above. Changing a filter will change the table as well as the points displayed on the map.
                 
                The points on the map represent COVID-19 patients' residences, or the places they have visited - depending on which option is selected. The color of the points represents how recent the cases are - redder points are more recent cases. 
                
                The data can be downloaded in CSV format by clicking the Download button.''',
                style = {'white-space': 'pre-line', 'text-align': 'justify'}),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close_info_button", className="ml-auto")
                ),
            ],
            id="info_modal",
        ),
        ],
        style=dict(
            height='2px',
            width='6%',
            display='table-cell',
            verticalAlign="middle",
        )),

        html.Div(
        [
            html.Button(
                "About",
                id="about_button",
                className="btn btn-primary",
                style=dict(height='30px', width = '80px', verticalAlign = 'middle')
            ),

            dbc.Modal(
            [
                dbc.ModalHeader("About"),
                dbc.ModalBody('''This app has been created by Isaac Tham, a Singaporean second-year undergraduate at the University of Pennsylvania. 
                
                Isaac is excited to hear from you and collaborate with like-minded data enthusiasts for the benefit of our society. Contact Isaac on email at isaactham2@hotmail.com or through Facebook.''',
                style = {'white-space': 'pre-line', 'text-align': 'justify'}),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close_about_button", className="ml-auto")
                ),
            ],
            id="about_modal",
        ),
        ],
        style=dict(
            height='2px',
            width='6%',
            display='table-cell',
            verticalAlign="middle",
        )),

        html.Div(
        [
            html.A(
                "Share on FB",
                href="http://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Fcovidsg.appspot.com%2F",
                className="btn btn-primary",
                target="_blank",
                style=dict(height='30px', width = '100px', verticalAlign = 'middle')
            )
        ],
        style=dict(
            height='2px',
            width='8%',
            display='table-cell',
            verticalAlign="middle",
        )),


        ], style = dict(
            width = '100%',
            display = 'table',
            verticalAlign = 'middle'
        ))

        ]
    ),
        html.Div([
            dcc.Dropdown(
                id = 'nationality_dropdown',
                options = [{'label': e, 'value': e} for e in df['nationality'].unique()],
                multi = True,
                value = [{'label': e, 'value': e} for e in df['nationality'].unique()],
                style = {'display': 'none'},
                placeholder = 'Choose nationalities...'
            )]),

    html.Div([
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
                {'name': 'Places Visited', 'id': 'places_visited'}
                ],
        data = [],
        style_data = {
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_cell = {
            'whiteSpace': 'normal',
            'font-family': 'Segoe UI',
            'font-size': '16px'
        },
        style_data_conditional = [
            {'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248'}
        ],
        style_cell_conditional = [
            {'if': {'column_id': 'case_num'},
            'width': '50px'},
            {'if': {'column_id': 'age'},
            'width': '60px'},
            {'if': {'column_id': 'gender'},
            'width': '80px'},
            {'if': {'column_id': 'hospital'},
            'width': '100px'},
            {'if': {'column_id': 'date_confirmed'},
            'width': '150px'},
            {'if': {'column_id': 'origin'},
            'width': '80px'},
            {'if': {'column_id': 'nationality'},
            'width': '150px'},
            {'if': {'column_id': 'residence'},
            'width': '350px'},
            {'if': {'column_id': 'places_visited'},
            'width': '350px'}
        ],
        style_table = {
            'height': '300px',
            'overflowX': 'scroll'},
        sort_action = 'native',
        #hidden_columns = ['residence_latitude', 'residence_longitude', 'date_confirmed_dt']
    )
    ], style = {'padding': '10px'}),

    html.Div([

        html.Div([
            html.H3(children = datetime.strftime(max_date, '%Y-%m-%d'), id = 'date_slider_display'),
            dcc.Slider(id = 'date_slider', 
                        min = 0, max = n_days, step = 1, value = 1,
                        updatemode = 'drag')
            ],
            style=dict(width='60%', display='table-cell', verticalAlign="middle")),

        html.Div([
            html.Button('Play', id = 'animation_play_pause_button',
                className="btn btn-primary",
                style=dict(height='30px', width = '60px', verticalAlign = 'middle')),
            dcc.Interval(id='date_slider_interval', interval = 1 * 1000, disabled=True),
            html.Div(id='date_slider_value_store', style={'display': 'none'})
        ], style = dict(width = '5%', verticalAlign = 'middle', display = 'table-cell')),

        html.Div(
            [html.Div('Speed'),
            dcc.Slider(id='animation_speed_slider', min=1, max=5, step=1, value=1,)
            ], style = dict(width = '10%', verticalAlign = 'middle', display = 'table-cell')
        ),

        html.Div([
        dcc.RadioItems(
            id = 'places_radio_button',
            options = [{'label': 'Residence', 'value': 'Residence'},
                        {'label': 'Places Visited', 'value': 'Places Visited'}],
            value = 'Residence',
            labelStyle = {'display': 'inline-block'}),

        ], style = dict(height = '10px', width = '15%', verticalAlign = 'middle', display = 'table-cell',
        fontsizeAdjust = '1.5', fontColor = 'blue'))
        
        ], style = {
            'width': '100%', 
            'verticalAlign': 'middle', 
            'display': 'table',
            'padding-top': '40px',
            'padding': '20px'}),

    html.Div(dcc.Graph(id='map'))
    ], style = {
        'padding': '20px'
    })

