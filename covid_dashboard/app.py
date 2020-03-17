### Contains the layout of the Dash app

from flask import Flask
from dash import Dash

server = Flask('project')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, server = server, external_stylesheets=external_stylesheets)

from covid_dashboard.layout import layout
app.layout = layout

from . import callbacks