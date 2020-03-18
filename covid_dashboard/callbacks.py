
from .app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
import io
import flask
import json


# Importing functions from other files
from .utilities import json_to_df

mapbox_access_token = "pk.eyJ1IjoidGhhbXN1cHBwIiwiYSI6ImNrN3Z4eTk2cTA3M2czbG5udDBtM29ubGIifQ.3UvulsJUb0FSLnAOkJiRiA"

ctx = dash.callback_context

# Read CSV
df = pd.read_csv('sg_covid_cases.csv')
residence_latitudes = df['residence_latitude'].dropna().tolist()
residence_longitudes = df['residence_longitude'].dropna().tolist()

# Hover text
df['hover_text'] = 'Case ' + df['case_num'].astype(str) + '<br /> ' + df['date_confirmed'] + '<br /> ' + df['residence']

# Change is_imported to Origin
df['origin'] = df['is_imported'].apply(lambda x: 'Imported' if x is True else 'Local')

# Check the number of days between today and first day
df['date_confirmed_dt'] = df['date_confirmed'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

max_date = df['date_confirmed_dt'].max()
min_date = df['date_confirmed_dt'].min()
n_days = (max_date - min_date).days + 1

centroid_latitude = 1.360085
centroid_longitude = 103.818654



### Test Callback which prints the dataframe to console at any one time
@app.callback(
    Output('filler', 'children'),
    [Input('print_df_button', 'n_clicks')],
)
def print_df(n_clicks):
    
    print(df)
    return None

### Test Callback which prints the dataframe to console at any one time
@app.callback(
    Output('filler2', 'children'),
    [Input('print_database_subset_button', 'n_clicks')],
    [State('database_subset', 'data')],
)
def print_database_subset(n_clicks, database_subset):
    
    database_subset = json_to_df(database_subset)
    print(database_subset)
    return None

### Tese Callback: From text input, calls PWBM and FRED Search API and sets the dropdown options for user to select variable to visualize
@app.callback(
    Output('output', 'children'),
    [Input('search_button', 'n_clicks')],
    [State('input', 'value')])
def set_display_text(search_button, input_value):

    return input_value

### CALLBACK : Sets the display of the date slider
@app.callback(
    Output('date_slider_display', 'children'),
    [Input('date_slider', 'value')]
)
def set_date_slider_display_text(date_slider_value):

    # Convert slider value to date
    return datetime.strftime((max_date - timedelta(days = (n_days - date_slider_value))), '%Y-%m-%d')

### CALLBACK : Sets the displays of the age range slider
@app.callback(
    Output('age_range_slider_display', 'children'),
    [Input('age_range_slider', 'value')]
)
def set_age_range_slider_display_text(age_range_slider_value):

    return 'Age Range: {} to {} Years'.format(age_range_slider_value[0], age_range_slider_value[1])


### CALLBACK 1: Filters the original database to form database_subset
@app.callback(
    Output('database_subset', 'data'),
    [Input('date_slider_display', 'children'),
    Input('age_range_slider', 'value'),
    Input('gender_checklist', 'value'),
    Input('origin_checklist', 'value'),
    Input('nationality_dropdown', 'value')]
)
def filter_database(date_slider_display, age_range_slider_value,
    gender_checklist_value, origin_checklist_value, nationality_dropdown_value):

    end_date = datetime.strptime(date_slider_display, '%Y-%m-%d')

    # Filter by date - starting point is original DF
    df_subset = df.loc[df['date_confirmed_dt'] <= end_date]

    # Filter by age range
    df_subset = df_subset.loc[(df_subset['age'] >= age_range_slider_value[0]) & 
    (df_subset['age'] <= age_range_slider_value[1]), :]

    # Filter by gender
    df_subset = df_subset.loc[df_subset['gender'].apply(lambda x: x in gender_checklist_value), :]

    # Filter by origin
    df_subset = df_subset.loc[df_subset['origin'].apply(lambda x: x in origin_checklist_value), :]

    # Filter by nationality
    df_subset = df_subset.loc[df_subset['nationality'].apply(lambda x: x in nationality_dropdown_value), :]

    # Get days before end_date
    df_subset['days_before_now'] = (end_date - df_subset['date_confirmed_dt']).apply(lambda x: -x.days)

    print('FILTER DATABASE TEST')

    return df_subset.to_json()

### CALLBACK 2: Updates the datatable from the filtered data in database_subset
@app.callback(
    Output('datatable', 'data'),
    [Input('database_subset', 'data')]
)
def update_datatable(df_subset):

    print('UPDATE DATATABLE STEST')

    df_subset = json_to_df(df_subset)

    datatable_data = df_subset.to_dict('records')

    return datatable_data


### CALLBACK 3: Draws the map
@app.callback(
    Output('map', 'figure'),
    [Input('database_subset', 'data')])
def draw_map_scatterplot(df_subset):

    df_subset = json_to_df(df_subset)

    data = [go.Scattermapbox(
            lat = df_subset['residence_latitude'], 
            lon = df_subset['residence_longitude'], 
            marker = {'color': df_subset['days_before_now'],
                    'colorscale': 'Reds',
                    'size': 8,
                    'opacity': 0.75},
            mode='markers', 
            text = df_subset['hover_text'], 
            hoverinfo='text', 
            name= 'COVID Cases')]

    return {"data": data,
            "layout": go.Layout(
                autosize=True, 
                hovermode='closest', 
                showlegend=False, 
                height=700,
                mapbox={
                    'accesstoken': mapbox_access_token, 
                    'bearing': 0, 
                    'center': {'lat': centroid_latitude, 'lon': centroid_longitude}, 
                    'pitch': 0, 'zoom': 10,
                    #"style": 'mapbox://styles/mapbox/streets-v11'
                    }
                )
            }

