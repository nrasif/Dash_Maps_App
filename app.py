import dash
from dash import Dash, html, dcc
from dash import html
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_leaflet as dl
from dash_extensions.javascript import arrow_function

from statistics import mean
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json

import geopandas as gpd

all_blocks = gpd.read_file('GeoJSON Files/blocks.geojson')
all_blocks['tooltip'] = '<STRONG> Block Name: </STRONG>' + all_blocks.Block_Name + '<BR><STRONG> Status: </STRONG>' + all_blocks.Status + '<BR><STRONG> Operator: </STRONG>' + all_blocks.Operator + '<BR><STRONG> Number of Wells: </STRONG>' + all_blocks.num_wells.astype(str) + '<BR><STRONG> Area in Sq. Kilometers </STRONG>' + all_blocks.sq_km.astype(str) + '<BR><STRONG> Estimated Reserves in Million of Barrels: </STRONG>'+ all_blocks.est_reserve.astype(str)

# -------------------------------------Dash Apps----------------------------------------

app = Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

app.layout = html.Section([
    html.Div(className='drawer',
            children=[
                
                dmc.Button("View Map Details", variant="outline", color='dark', radius='10px', id='open-drawer', className='drawer-button-1',leftIcon=DashIconify(icon='material-symbols:map-outline', width=25),
                           style={
                    "transform": "rotate(270deg)",
                    "position":"absolute",
                    "top": "450px",
                    "left": "-19px"
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
                                                                    value=all_blocks['Block_Name'].unique().tolist(),
                                                                    data=all_blocks['Block_Name'].unique().tolist(),
                                                                    style={'marginTop':10},
                                                                    clearable=True,
                                                                    searchable=True,
                                                                    nothingFound= 'No Options Found'
                                                                    ),
                                                                dmc.Text(id='output-block'), #output for multi-select
                                                                
                                                                html.H5('Status', style={'marginTop':20}),
                                                                dmc.CheckboxGroup(
                                                                    id='checkbox_status_block',
                                                                    orientation='vertical',
                                                                    children=[
                                                                        dmc.Checkbox(label='Exploration',value='Exploration',color='dark', style={'marginTop':0}),
                                                                        dmc.Checkbox(label='Development',value='Development',color='dark', style={'marginTop':-15}),
                                                                        dmc.Checkbox(label='Production',value='Production',color='dark', style={'marginTop':-15}),
                                                                        dmc.Checkbox(label='Abandoned',value='Abandoned',color='dark', style={'marginTop':-15})
                                                                    ],
                                                                    value=['Exploration','Development','Production','Abandoned']
                                                                ),
                                                                
                                                                html.H5('Operator Name', style={'marginTop':20}),
                                                                dmc.MultiSelect(
                                                                    placeholder="Select Operator Name",
                                                                    id="multiselect-operator",
                                                                    value=all_blocks['Operator'].unique().tolist(),
                                                                    data=all_blocks['Operator'].unique().tolist(),
                                                                    style={'marginTop':10},
                                                                    clearable=True,
                                                                    searchable=True,
                                                                    nothingFound= 'No Options Found'
                                                                    ),
                                                                dmc.Text(id='output-operator'), #output for multi-select

                                                                html.H5('Number of Wells', style={'marginTop':20}),
                                                                dmc.RangeSlider(
                                                                    id='num-wells',
                                                                    value=[all_blocks['num_wells'].min(), all_blocks['num_wells'].max()],
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
                                                                    id='km-slider',
                                                                    value=[all_blocks['sq_km'].min(), all_blocks['sq_km'].max()],
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
                                                                    value=[all_blocks['est_reserve'].min(), all_blocks['est_reserve'].max()],
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
                                                                
                                                                dmc.Button('Reset', id='reset-block', variant='outline', color='dark', radius='10px', leftIcon=DashIconify(icon='material-symbols:restart-alt', width=25), 
                                                                           style={'marginTop':'25px'})
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
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_orientation_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Exploration',value='Exploration',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Development',value='Development',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Appraisal',value='Appraisal',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Monitoring',value='Monitoring',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=[]
                                                        ),

                                                        html.H5('Status', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_status_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Active',value='Active',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Inactive',value='Inactive',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Suspended',value='Suspended',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Abandoned',value='Abandoned',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=[]
                                                        ),

                                                        html.H5('Purpose', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_purpose_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Exploration',value='Exploration',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Development',value='Development',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Appraisal',value='Appraisal',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Monitoring',value='Monitoring',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=[]
                                                        ),

                                                        html.H5('Type', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_type_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Oil',value='Oil',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Gas',value='Gas',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Injection',value='Injection',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Observation',value='Observation',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=[]
                                                        )

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
    id='output-map'
),
    html.Div(
        className='dashboard-content',
        children=[
            
            dmc.Button("View Dashboard Details", variant="outline", color='dark', id='open-drawer-2', className='icon-button-2',radius='10px', leftIcon=DashIconify(icon='mdi:graph-pie-outline', width=25), 
                       style={
                "transform": "rotate(270deg)",
                "position":"absolute",
                "top": "1000px",
                "left": "-48px"
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
    Output('multiselect-block','data'),
    Input('num-wells','value'),
    Input('km-slider','value'),
    Input('range-slider-reserve','value'),
    Input('checkbox_status_block','value'),
    Input('multiselect-operator', 'value')
)

def set_block_option(chosen_numwell, chosen_km, chosen_reserve, chosen_status, chosen_operator):
    df_block = all_blocks[(all_blocks['num_wells'].between(chosen_numwell[0], chosen_numwell[1])) & (all_blocks['sq_km'].between(chosen_km[0], chosen_km[1])) & (all_blocks['est_reserve'].between(chosen_reserve[0], chosen_reserve[1])) & (all_blocks['Status'].isin(chosen_status)) & (all_blocks['Operator'].isin(chosen_operator))]
    return pd.unique(df_block['Block_Name'].to_list())

@app.callback(
    Output('multiselect-block','value'),
    Output('num-wells','value'),
    Output('km-slider','value'),
    Output('range-slider-reserve','value'),
    Output('checkbox_status_block','value'),
    Output('multiselect-operator','value'),
    Input('reset-block','n_clicks')
)

def reset_filter_block(clicked):
    
    reset_df = all_blocks[(all_blocks['num_wells'].between(all_blocks['num_wells'].min(), all_blocks['num_wells'].max())) & (all_blocks['sq_km'].between(all_blocks['sq_km'].min(), all_blocks['sq_km'].max())) & (all_blocks['est_reserve'].between(all_blocks['est_reserve'].min(), all_blocks['est_reserve'].max())) & (all_blocks['Status'].isin(all_blocks['Status'])) & (all_blocks['Operator'].isin(all_blocks['Operator']))]
    reset_block_name = pd.unique(reset_df['Block_Name'].to_list())
    reset_num_blocks = reset_df['num_wells'].min(), reset_df['num_wells'].max()
    reset_km_blocks = reset_df['sq_km'].min(), reset_df['sq_km'].max()
    reset_reserve_blocks = reset_df['est_reserve'].min(), reset_df['est_reserve'].max()
    reset_status_blocks = ['Exploration','Development','Production','Abandoned']
    reset_operator_blocks = pd.unique(reset_df['Operator'].to_list())
    
    return reset_block_name, reset_num_blocks, reset_km_blocks, reset_reserve_blocks, reset_status_blocks, reset_operator_blocks

@app.callback(
    Output('output-map','children'),
    Input('multiselect-block','value'),
    Input('multiselect-block','data')
)

def plot_map(block_submitted_value, block_submitted_data):
    edited_layer= all_blocks[(all_blocks['Block_Name'].isin(block_submitted_value)) & (all_blocks['Block_Name'].isin(block_submitted_data))]
    if edited_layer.empty:
        # Generate map without polygons
        return dl.Map([dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
                        dl.GestureHandling()],
                        center=[5.3, 96.3],
                        zoom=10,
                        style={
                            'z-index':'0',
                            'width': '1750px',
                            'height': '965px',
                            'marginLeft':'20px',
                        })

    layer_blocks = dl.GeoJSON(id='block_load',
                        data=json.loads(edited_layer.to_json()),
                        hoverStyle=arrow_function(dict(weight=6, fillColor='#3F72AF')),
                        options=dict(style=dict(color='#ADD8E6', 
                                    weight=2, 
                                    dashArray='30, 10',
                                    dashOffset='1',
                                    opacity=1,
                                    )))
    bounds = edited_layer.total_bounds
    x = mean([bounds[0], bounds[2]])
    y = mean([bounds[1], bounds[3]])
    location = (y, x)
    
    return dl.Map([dl.GeoJSON(layer_blocks),
                    dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'), 
                    dl.GestureHandling()],
                    center=[y, x],
                    zoom=10,
                    style={
                        'z-index':'0',
                        'width': '1750px',
                        'height': '965px',
                        'marginLeft':'20px',
                    })


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
    app.run_server(debug=True, port = 1514)