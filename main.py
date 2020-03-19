### Contains the layout of the Dash app

from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

flask_app = Flask(__name__)

external_stylesheets = [dbc.themes.LUMEN]

meta_tags = [
    {'property': 'og:image',
    'content': 'https://www.todayonline.com/sites/default/files/styles/new_app_article_detail/public/19356685_0.PNG?itok=yph1Myl7'}
]


app = Dash(__name__, server = flask_app, external_stylesheets=external_stylesheets, meta_tags = meta_tags)

from layout import layout
app.layout = layout
app.title = 'Singapore COVID-19 Cases'

from callbacks import *

server = app.server


if __name__ == '__main__':
    app.run_server(debug = False)