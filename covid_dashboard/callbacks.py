
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

### CALLBACK 1: From text input, calls PWBM and FRED Search API and sets the dropdown options for user to select variable to visualize
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


### CALLBACK 2: Draws the map

@app.callback(
    Output('map', 'figure'),
    [Input('search_button', 'n_clicks'),
    Input('date_slider_display', 'children'),
    Input('datatable', 'selected_rows')])
def draw_map_scatterplot(search_button, date_slider_display, datatable_selected_rows):

    end_date = datetime.strptime(date_slider_display, '%Y-%m-%d')

    # Filter by selected rows
    df_subset = df.iloc[datatable_selected_rows, :]

    # Filter by date
    df_subset = df_subset.loc[df_subset['date_confirmed_dt'] <= end_date]

    # Get days before end_date
    df_subset['days_before_now'] = (end_date - df_subset['date_confirmed_dt']).apply(lambda x: -x.days)

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

