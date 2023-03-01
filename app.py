import dash
from dash import Dash, html, dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np


# -------------------------------------Dash Apps----------------------------------------

app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

app.layout = html.Section([
    html.Div(
        className="content1",
        children=[
            html.H1('Dummy Block', className="title-block"),
            html.H4('Summary'),
            html.P('This block data are dummy, intended for testing purposes. All blocks are not representing the real conditions')
        ]
    ),
    html.Div(
        className="content2",
        
        )
    
    ])

if __name__ == '__main__':
    app.run_server(debug=True)