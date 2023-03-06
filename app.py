import dash
from dash import Dash, html, dcc
from dash import html
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
import numpy as np


# -------------------------------------Dash Apps----------------------------------------

app = Dash(__name__, meta_tags=[
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
    dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.Tab("Info", icon=DashIconify(icon="bi:info-circle", width=15), value="info"),
                dmc.Tab("Filter",icon=DashIconify(icon="tabler:settings", width=20), value="filter"),
                dmc.Tab("Download", icon=DashIconify(icon="material-symbols:cloud-download-outline", width=20), value="download"),
            ]
        ),
        dmc.TabsPanel(
            html.Div(
                className="tab1-content",
                children=[
                    html.H4('Details'),
                    DashIconify(icon='mdi:database-arrow-down-outline', width=40, className='db_icon'),
                    html.H5('Feature layer'),
                    html.P('Dataset'),
                    
                    DashIconify(icon='material-symbols:info-outline', width=40, className='info_icon'),
                    html.H5('Updated info'),
                    html.P('03 February 2023'),
                    
                    DashIconify(icon='material-symbols:date-range-outline', width=40, className='date_icon'),
                    html.H5('Publication date'),
                    html.P('04 February 2023'),
                    
                    DashIconify(icon='mdi:world', width=40, className='world_icon'),
                    html.H5('Anyone can view this content'),
                    html.P('Public'),
                    
                    DashIconify(icon='material-symbols:lock-outline', width=40, className='lock_icon'),
                    html.H5('Request permission to use'),
                    html.P('No License')
            ]),
            value="info"),
        dmc.TabsPanel(
            html.Div(
                className="table2-content",
                children=[
                    dmc.MultiSelect(
                        label="Block Name",
                        placeholder="Select Block Name",
                        id="multiselect-block",
                        value=['test1','test2'])
                    ]),
            value="filter"),
        dmc.TabsPanel("test3", value="download"),
    ],
    color="dark",
    persistence_type="session",
    value="info",
    variant="pills",
    className="main-tabs"
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)