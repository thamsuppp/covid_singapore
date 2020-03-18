### Contains the layout of the Dash app

from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

server = Flask('project')

external_stylesheets = [dbc.themes.LITERA]
app = Dash(__name__, server = server, external_stylesheets=external_stylesheets)

from covid_dashboard.layout import layout
app.layout = layout

from . import callbacks