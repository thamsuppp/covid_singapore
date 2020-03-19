### Contains the layout of the Dash app

from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

server = Flask('project')

external_stylesheets = [dbc.themes.LUMEN]
app = Dash(__name__, server = server, external_stylesheets=external_stylesheets)

from layout import layout
app.layout = layout

from callbacks import *

if __name__ == '__main__':
    app.run_server()