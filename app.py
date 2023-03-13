import dash
from dash import Dash, html, dcc
from dash import html
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_leaflet as dl
from dash_extensions.javascript import arrow_function

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json

import geopandas as gpd

all_blocks = gpd.read_file('GeoJSON Files/blocks.geojson')
all_blocks['tooltip'] = '<STRONG> Block Name: </STRONG>' + all_blocks.Block_Name + '<BR><STRONG> Status: </STRONG>' + all_blocks.Status + '<BR><STRONG> Operator: </STRONG>' + all_blocks.Operator + '<BR><STRONG> Number of Wells: </STRONG>' + all_blocks.num_wells.astype(str) + '<BR><STRONG> Area in Sq. Kilometers </STRONG>' + all_blocks.sq_km.astype(str) + '<BR><STRONG> Estimated Reserves in Million of Barrels: </STRONG>'+ all_blocks.est_reserve.astype(str)
layer_blocks = dl.GeoJSON(id='block',
                        data=json.loads(all_blocks.to_json()),
                        hoverStyle=arrow_function(dict(weight=6, fillColor='#3F72AF')),
                        options=dict(style=dict(color='#ADD8E6', 
                                    weight=2, 
                                    dashArray='30, 10',
                                    dashOffset='1',
                                    opacity=1,
                                    )))





# -------------------------------------Dash Apps----------------------------------------

app = Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

app.layout = html.Section([
    html.Div(className='drawer',
            children=[
                
                dmc.Button("View Map Details", variant="outline", color='dark', id='open-drawer', className='drawer-button-1', style={
                    "transform": "rotate(270deg)",
                    "position":"absolute",
                    "top": "450px",
                    "left": "0px"
                    }),
                dmc.Drawer(
                    id='drawer',
                    size='630px',
                    lockScroll=False,
                    zIndex=999,
                    overlayOpacity=0,
                    className='drawer-class',
                    transition='slide-right',
                    transitionDuration=500,
                    
                    children=[
                         html.Div(
                            className="content1",
                            children=[
                                html.H1('Dummy Block', className="title-block"),
                                html.H4('Summary'),
                                html.P('This block data are dummy, intended for testing purposes. All blocks are not representing the real conditions.')
                            ]
                        ),
                        dmc.Tabs(
                        [
                            dmc.TabsList(
                                [
                                    dmc.Tab("Info", icon=DashIconify(icon="material-symbols:info-outline", width=20), value="info"),
                                    dmc.Tab("Filter",icon=DashIconify(icon="mdi:funnel-cog-outline", width=20), value="filter"),
                                    dmc.Tab("Download", icon=DashIconify(icon="material-symbols:cloud-download-outline", width=20), value="download"),
                                ]
                            ),
                            dmc.TabsPanel(
                                html.Div(
                                    className="tab1-content",
                                    children=[

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
                                        html.P('No License'),

                                        dmc.Button('View full details', variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='material-symbols:picture-as-pdf-outline',width=25), 
                                        style={'marginTop':30})
                                ]),
                                value="info"),

                            dmc.TabsPanel(
                                html.Div(
                                    className="table2-content",
                                    children=[
                                        
                                        dmc.Accordion(
                                            value='block_filter_val',
                                            style={'marginTop':30},
                                            radius=10,
                                            children=[dmc.AccordionItem(
                                                [
                                                    dmc.AccordionControl('Block Filter', icon=DashIconify(icon='mdi:surface-area',width=20)),
                                                    dmc.AccordionPanel(
                                                        html.Div(
                                                            className='accordion-content',
                                                            children=[
                                                                html.H5('Block Name', style={'marginTop':20}),
                                                                dmc.MultiSelect(
                                                                    placeholder="Select Block Name",
                                                                    id="multiselect-block",
                                                                    value=all_blocks['Block_Name'].to_list(),
                                                                    data=all_blocks['Block_Name'].to_list(),
                                                                    style={'marginTop':10},
                                                                    clearable=True,
                                                                    searchable=True,
                                                                    nothingFound= 'No Options Found'
                                                                    ),
                                                                dmc.Text(id='output-block'), #output for multi-select
                                                                
                                                                html.H5('Status', style={'marginTop':20}),
                                                                dmc.Checkbox(id='checkbox-1', label='Exploration',color='dark', checked=True, style={'marginTop':10}),
                                                                dmc.Text(id='output-checkbox-1'), #output for checkbox 1
                                                                dmc.Checkbox(id='checkbox-2', label='Development',color='dark', checked=True, style={'marginTop':5}),
                                                                dmc.Text(id='output-checkbox-2'), #output for checkbox 2
                                                                dmc.Checkbox(id='checkbox-3', label='Production',color='dark', checked=True, style={'marginTop':5}),
                                                                dmc.Text(id='output-checkbox-3'), #output for checkbox 1
                                                                dmc.Checkbox(id='checkbox-4', label='Abandoned',color='dark', checked=True, style={'marginTop':5}),
                                                                dmc.Text(id='output-checkbox-4'), #output for checkbox 2
                                                                
                                                                html.H5('Operator Name', style={'marginTop':20}),
                                                                dmc.MultiSelect(
                                                                    placeholder="Select Operator Name",
                                                                    id="multiselect-operator",
                                                                    value=pd.unique(all_blocks['Operator'].to_list()),
                                                                    data=pd.unique(all_blocks['Operator'].to_list()),
                                                                    style={'marginTop':10},
                                                                    clearable=True,
                                                                    searchable=True,
                                                                    nothingFound= 'No Options Found'
                                                                    ),
                                                                dmc.Text(id='output-operator'), #output for multi-select

                                                                html.H5('Number of Wells', style={'marginTop':20}),
                                                                dmc.RangeSlider(
                                                                    id='num-wells',
                                                                    value=[0, 20],
                                                                    max=60,
                                                                    min=0,
                                                                    marks=[
                                                                        {'value':10, 'label':'10'},
                                                                        {'value':30, 'label':'30'},
                                                                        {'value':50, 'label':'50'}
                                                                        ],
                                                                    style={'marginTop':10, 'marginBottom':30},
                                                                    color='dark'),
                                                                dmc.Text(id='output-slider-num-wells'), #output for range slider
                                                                
                                                                html.H5('Shape Area in Sq. Kilometers', style={'marginTop':20}),
                                                                dmc.RangeSlider(
                                                                    id='range-slider',
                                                                    value=[126, 220],
                                                                    max=350,
                                                                    min=0,
                                                                    marks=[
                                                                        {'value':50, 'label':'50'},
                                                                        {'value':150, 'label':'150'},
                                                                        {'value':250, 'label':'250'}
                                                                        ],
                                                                    style={'marginTop':10, 'marginBottom':30},
                                                                    color='dark'),
                                                                dmc.Text(id='output-slider'), #output for range slider

                                                                html.H5('Estimated Reserves in Millions of Barrels Oil', style={'marginTop':20}),
                                                                dmc.RangeSlider(
                                                                    id='range-slider-reserve',
                                                                    value=[0, 500],
                                                                    max=600,
                                                                    min=0,
                                                                    marks=[
                                                                        {'value':100, 'label':'100'},
                                                                        {'value':300, 'label':'300'},
                                                                        {'value':500, 'label':'500'}
                                                                        ],
                                                                    style={'marginTop':10, 'marginBottom':30},
                                                                    color='dark'),
                                                                dmc.Text(id='output-slider-reserve'), #output for range slider
                                                            ]
                                                        )
                                                    )
                                                ], value='block_filter_val'
                                            )
                                            ], variant='contained'
                                        ),
                                        
                                        dmc.Accordion(
                                            value='wellhead_val',
                                            style={'marginTop':10, 'marginBottom':20},
                                            radius=10,
                                            children=[dmc.AccordionItem(
                                                [
                                                    dmc.AccordionControl('Well Filter', icon=DashIconify(icon='material-symbols:pin-drop-outline',width=20)),
                                                    dmc.AccordionPanel(
                                                        html.Div(
                                                            className='accordion_content2',
                                                            children=[
                                                        html.H5('Well Name', style={'marginTop':20}),
                                                        dmc.MultiSelect(
                                                            placeholder="Select Borehole Name",
                                                            id="multiselect-borehole",
                                                            value=['test1'],
                                                            data=['test1','test2'],
                                                            style={'marginTop':10},
                                                            clearable=True,
                                                            searchable=True,
                                                            nothingFound= 'No Options Found'
                                                            ),
                                                        dmc.Text(id='output-borehole'), #output for multi-select
                                                        
                                                        html.H5('TVDSS in Meters', style={'marginTop':20}),
                                                        dmc.RangeSlider(
                                                            id='range-slider-TVDSS',
                                                            value=[500,2000],
                                                            max=5000,
                                                            min=0,
                                                            marks=[
                                                                {'value':2000, 'label':'2000m'},
                                                                {'value':4000, 'label':'4000m'},
                                                                ],
                                                            style={'marginTop':10},
                                                            color='dark'),
                                                        dmc.Text(id='output-porosity'), #output for slider porosity

                                                        html.H5('Wellbore Orientation', style={'marginTop':30}),
                                                        dmc.Checkbox(id='checkbox-or1', label='Vertical',color='dark', checked=True, style={'marginTop':10}),
                                                        dmc.Text(id='output-checkbox-or1'), #output for checkbox 1
                                                        dmc.Checkbox(id='checkbox-or2', label='Directional',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-or2'), #output for checkbox 2
                                                        dmc.Checkbox(id='checkbox-or3', label='Horizontal',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-or3'), #output for checkbox 3

                                                        html.H5('Status', style={'marginTop':20}),
                                                        dmc.Checkbox(id='checkbox-stat1', label='Active',color='dark', checked=True, style={'marginTop':10}),
                                                        dmc.Text(id='output-checkbox-stat'), #output for checkbox 1
                                                        dmc.Checkbox(id='checkbox-stat2', label='Inactive',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-stat2'), #output for checkbox 2
                                                        dmc.Checkbox(id='checkbox-stat3', label='Suspended',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-stat3'), #output for checkbox 3
                                                        dmc.Checkbox(id='checkbox-stat4', label='Abandoned',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-stat4'), #output for checkbox 4

                                                        html.H5('Purpose', style={'marginTop':20}),
                                                        dmc.Checkbox(id='checkbox-purpose1', label='Exploration',color='dark', checked=True, style={'marginTop':10}),
                                                        dmc.Text(id='output-checkbox-purpose1'), #output for checkbox 1
                                                        dmc.Checkbox(id='checkbox-purpose2', label='Development',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-purpose2'), #output for checkbox 2
                                                        dmc.Checkbox(id='checkbox-purpose3', label='Appraisal',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-purpose3'), #output for checkbox 3
                                                        dmc.Checkbox(id='checkbox-purpose4', label='Monitoring',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-purpose4'), #output for checkbox 4

                                                        html.H5('Type', style={'marginTop':20}),
                                                        dmc.Checkbox(id='checkbox-type1', label='Oil',color='dark', checked=True, style={'marginTop':10}),
                                                        dmc.Text(id='output-checkbox-type1'), #output for checkbox 1
                                                        dmc.Checkbox(id='checkbox-type2', label='Gas',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-type2'), #output for checkbox 2
                                                        dmc.Checkbox(id='checkbox-type3', label='Injection',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-type3'), #output for checkbox 3
                                                        dmc.Checkbox(id='checkbox-type4', label='Observation',color='dark', checked=True, style={'marginTop':5}),
                                                        dmc.Text(id='output-checkbox-type4'), #output for checkbox 4
                                                        

                                                            ]
                                                        )
                                                    )
                                                ], value='wellhead_val'
                                            )
                                            ], variant='contained'
                                        )
                                        
                                        ]),
                                value="filter"),
                                
                                dmc.TabsPanel(
                                    html.Div(
                                    className='table3-content',
                                    children=[
                                        dmc.Button('Download data as CSV', variant='outline',color='dark',radius='10px', leftIcon=DashIconify(icon='ph:file-csv',width=25),style={'marginTop':25}),
                                        html.Br(),
                                        dmc.Button('Download data as GeoJSON', variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='mdi:code-json',width=25), style={'marginTop':10}),
                                        html.Br(),
                                        dmc.Button('Download data as SHP', variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='gis:shape-file',width=25), style={'marginTop':10})
                                    ]
                                    )
                        ,value="download"),
                        ],
                        color="dark",
                        persistence_type="session",
                        value="info",
                        variant="pills",
                        className="main-tabs",
                        radius=10
                        ),
                     ] #closing children parameter for drawer
                 ) #closing dmc.drawer
                
             ]), #closing first div (drawer)
    html.Div(
    className='content2',
    children=[
        
        dl.Map([layer_blocks, dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'), dl.GestureHandling(), dl.FullscreenControl()],
                center=[5.3, 96.3],
                zoom=11,
                style={
                    'z-index':'0',
                    'width': '1787px',
                    'height': '965px',
                    'marginLeft':'20px',
                })
    ]
),
    html.Div(
        className='dashboard-content',
        children=[
            
            dmc.Button("View Dashboard Details", variant="outline", color='dark', id='open-drawer-2', className='icon-button-2', style={
                "transform": "rotate(270deg)",
                "position":"absolute",
                "top": "1000px",
                "left": "-25px"
                }),
            dmc.Drawer(
                    id='drawer-2',
                    size='630px',
                    lockScroll=False,
                    zIndex=999,
                    overlayOpacity=0,
                    className='drawer-class',
                    transition='slide-right',
                    transitionDuration=500)
        ]
    )
])

@app.callback(
    Output("drawer", "opened"),
    Input("open-drawer", "n_clicks"),
    prevent_initial_call=True
)

@app.callback(
    Output('drawer-2','opened'),
    Input('open-drawer-2','n_clicks'),
    prevent_initial_call=True
)

def drawer(n_clicks):
    return True

if __name__ == '__main__':
    app.run_server(debug=True)