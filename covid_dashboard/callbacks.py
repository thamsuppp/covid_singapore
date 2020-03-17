
from .app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, date, time
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

centroid_latitude = 1.360085
centroid_longitude = 103.818654

# Hover text
df['hover_text'] = 'Case ' + df['case_num'].astype(str) + '<br /> ' + df['date_confirmed'] + '<br /> ' + df['residence']

### CALLBACK 1: From text input, calls PWBM and FRED Search API and sets the dropdown options for user to select variable to visualize
@app.callback(
    Output('output', 'children'),
    [Input('search_button', 'n_clicks')],
    [State('input', 'value')])
def set_display_text(search_button, input_value):

    return input_value


### CALLBACK 2: Draws the map

@app.callback(
    Output('map', 'figure'),
    [Input('search_button', 'n_clicks'),
    Input('datatable', 'selected_rows')])
def draw_map_scatterplot(search_button, datatable_selected_rows):

    print(datatable_selected_rows)

    # Filter by selected rows
    df_subset = df.iloc[datatable_selected_rows, :]

    data = [go.Scattermapbox(
            lat = df_subset['residence_latitude'], 
            lon= df_subset['residence_longitude'], 
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

