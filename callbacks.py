
from main import app
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
import urllib
from urllib.parse import quote, urlparse, parse_qsl, urlencode
from random import random
import io
import flask
import json
from sqlalchemy import create_engine

from layout import connection

# Importing functions from other files
from utilities import json_to_df

mapbox_access_token = "pk.eyJ1IjoidGhhbXN1cHBwIiwiYSI6ImNrN3Z4eTk2cTA3M2czbG5udDBtM29ubGIifQ.3UvulsJUb0FSLnAOkJiRiA"

ctx = dash.callback_context

# Read Cases
df = pd.read_sql_query('SELECT * FROM cases', connection)
df['is_imported'] = df['is_imported'].apply(lambda x: True if x == '1' else False)

# Change is_imported to Origin
df['origin'] = df['is_imported'].apply(lambda x: 'Imported' if x is True else 'Local')
# Check the number of days between today and first day
df['date_confirmed_dt'] = df['date_confirmed'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

max_date = df['date_confirmed_dt'].max()
min_date = df['date_confirmed_dt'].min()
n_days = (max_date - min_date).days + 1

centroid_latitude = 1.360085
centroid_longitude = 103.818654

# Read places visited CSV
places_df = pd.read_csv('sg_covid_places_visited.csv')

#Add random jitter 
df['residence_latitude'] = df['residence_latitude'].apply(lambda x: x + (random() - 0.5) / 1000)
df['residence_longitude'] = df['residence_longitude'].apply(lambda x: x + (random() - 0.5) / 1000)
places_df['place_latitude'] = places_df['place_latitude'].apply(lambda x: x + (random() - 0.5) / 1000)
places_df['place_longitude'] = places_df['place_longitude'].apply(lambda x: x + (random() - 0.5) / 1000)

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
    selected_nationalities = [e for e in nationality_dropdown_value]
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
    df_subset = df_subset.loc[df_subset['nationality'].apply(lambda x: x in selected_nationalities), :]
    # Get days before end_date
    df_subset['days_before_now'] = (end_date - df_subset['date_confirmed_dt']).apply(lambda x: -x.days)

    return df_subset.to_json()

### CALLBACK 2: Updates the datatable from the filtered data in database_subset
@app.callback(
    Output('datatable', 'data'),
    [Input('database_subset', 'data')]
)
def update_datatable(df_subset):

    df_subset = json_to_df(df_subset)
    datatable_data = df_subset.to_dict('records')

    return datatable_data


### CALLBACK 3: Draws the map - THIS IS WHERE PLACES_DF IS MERGED
@app.callback(
    Output('map', 'figure'),
    [Input('database_subset', 'data'),
    Input('places_radio_button', 'value')])
def draw_map_scatterplot(df_subset, places_radio_button_value):

    df_subset = json_to_df(df_subset)


    # Display places visited
    if places_radio_button_value == 'Places Visited':
        df_subset = df_subset.merge(places_df, how = 'left', on = 'case_num')

        lat = df_subset['place_latitude']
        lon = df_subset['place_longitude']

        df_subset['hover_text'] = 'Case ' + df_subset['case_num'].astype(str) + \
        '<br /> ' + df_subset['date_confirmed'] + '<br /> ' + df_subset['places_visited_list']

    elif places_radio_button_value == 'Residence':

        lat = df_subset['residence_latitude']
        lon = df_subset['residence_longitude']

        df_subset['hover_text'] = 'Case ' + df_subset['case_num'].astype(str) + \
        '<br /> ' + df_subset['date_confirmed'] + '<br /> ' + df_subset['residence']

    data = [go.Scattermapbox(
            lat = lat, 
            lon = lon, 
            marker = {'color': df_subset['days_before_now'],
                    'colorscale': 'reds',
                    'cmin': -n_days - 5,
                    'cmax': n_days / 3,
                    'size': 12,
                    'opacity': 1},
            mode='markers', 
            text = df_subset['hover_text'], 
            hoverinfo='text', 
            name= 'COVID Cases')]

    return {"data": data,
            "layout": go.Layout(
                height = 800,
                width = 1450,
                margin={'l': 50, 'r': 50, 't': 0, 'b': 0},
                hovermode='closest', 
                showlegend=False, 
                mapbox={
                    'accesstoken': mapbox_access_token, 
                    'bearing': 0, 
                    'center': {'lat': centroid_latitude, 'lon': centroid_longitude}, 
                    'pitch': 0, 'zoom': 11,
                    'style': 'mapbox://styles/mapbox/outdoors-v11'
                    }
                )
            }


### CALLBACK : Animates the map by incrementing the date at regular intervals
@app.callback(
    Output('date_slider', 'value'),
    [Input('date_slider_interval', 'n_intervals')],
    [State('date_slider', 'value'),
     State('date_slider', 'max'),
     State('date_slider', 'min')]
)
def animate_map(n_intervals, slider_value, slider_max, slider_min):
    if ctx.triggered[0]['prop_id'] == 'date_slider_value_store.children':
        return 0
    else:
        if slider_value >= slider_max:
            return slider_min
        else:
            return slider_value + 1

#CALLBACK 7.3: Enables or disables the interval timer when the play/pause button is activated respectively
@app.callback(
    [Output('date_slider_interval', 'disabled'),
     Output('animation_play_pause_button', 'children')],
    [Input('animation_play_pause_button', 'n_clicks')],
    [State('date_slider_interval', 'disabled')]
)
def play_pause_animation(play_pause_button, is_disabled):
    if ctx.triggered == []:
        return True, 'Play'
    #If play/pause button is pressed
    elif ctx.triggered[0]['prop_id'].split('.')[0] == 'animation_play_pause_button':
        if is_disabled == True:
            return (not is_disabled), 'Pause'
        else:
            return (not is_disabled), 'Play'

# CALLBACK 7.4: Changes animation speed depending on animation speed slider
@app.callback(
    Output('date_slider_interval', 'interval'),
    [Input('animation_speed_slider', 'value')]
)
def change_animation_speed(slider_value):
    interval = (15 - 2 * slider_value) * 100
    return interval



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

### CALLBACK : Selects all nationalities if the checkbox is checked
@app.callback(
    Output('nationality_dropdown', 'value'),
    [Input('select_all_nationality_checklist', 'value')]
)
def set_all_nationality_dropdown(checkbox_value):
    print(checkbox_value)
    if checkbox_value == ['All']:
        return [e for e in df['nationality'].unique()]

    else:
        return []


#CALLBACK : Updates the download link when df-store is updated to allow user to download data as CSV
@app.callback(
    Output("download-link", "href"),
    [Input('database_subset', 'data')])

def update_download_link(database_subset):
    df = json_to_df(database_subset)

    df = df.rename(columns = {'case_num': 'No.', 'age': 'Age', 'gender': 'Gender', 'hospital': 'Hospital', 
                'date_confirmed': 'Date Confirmed', 'nationality': 'Nationality', 'origin': 'Origin',
                'residence': 'Residence', 'places_visited': 'Places Visited'})

    df = df.loc[: , ['No.', 'Age', 'Gender', 'Hospital', 'Date Confirmed', 'Nationality', 'Origin',
                'Residence', 'Places Visited']]

    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

    return csv_string

# CALLBACK : Makes the nationality dropdown disappear if the select_all_nationality_checklist is checked
@app.callback(
    Output('nationality_dropdown', 'style'),
    [Input('select_all_nationality_checklist', 'value')]
)
def change_nationality_dropdown_visibility(checkbox_value):

    print(checkbox_value)
    if checkbox_value == ['All']:
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'width': '100%'}



@app.callback(
    Output("info_modal", "is_open"),
    [Input("info_button", "n_clicks"), 
    Input("close_info_button", "n_clicks")],
    [State("info_modal", "is_open")],
)
def toggle_info_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("about_modal", "is_open"),
    [Input("about_button", "n_clicks"), 
    Input("close_about_button", "n_clicks")],
    [State("about_modal", "is_open")],
)
def toggle_about_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open