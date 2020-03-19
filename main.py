### Contains the layout of the Dash app

from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

flask_app = Flask(__name__)

external_stylesheets = [dbc.themes.LUMEN]
app = Dash(__name__, server = flask_app, external_stylesheets=external_stylesheets)

from layout import layout
app.layout = layout

from callbacks import *

server = app.server


if __name__ == '__main__':
    app.run_server(debug = False)