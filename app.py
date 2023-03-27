import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_leaflet as dl
from dash_extensions.javascript import arrow_function, assign
from dash.exceptions import PreventUpdate

from statistics import mean
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json
import zipfile

import geopandas as gpd

all_blocks = gpd.read_file('GeoJSON Files/blocks.geojson')
all_wells = gpd.read_file('GeoJSON Files/wells.geojson')

all_blocks['tooltip'] = all_blocks['Block_Name']
all_wells['tooltip'] = all_wells['Well_Name']

# Write the data to a Shapefile (blocks)
all_blocks.to_file('SHP files/all_blocks/all_blocks.shp')
# Create a ZIP file containing all the Shapefile files
with zipfile.ZipFile('SHP zipfile/all_blocks.zip', 'w') as zip:
    for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg']:
        filename = 'SHP files/all_blocks{}'.format(ext)
        if os.path.exists(filename):
            zip.write(filename)


# Write the data to a Shapefile (wells)
all_wells.to_file('SHP files/all_wells/all_wells.shp')
# Create a ZIP file containing all the Shapefile files
with zipfile.ZipFile('SHP zipfile/wells.zip', 'w') as zip:
    for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg']:
        filename = 'SHP files/wells{}'.format(ext)
        if os.path.exists(filename):
            zip.write(filename)
            
layout_data = [['Satellite','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}','dark'],
               ['Dark','https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png','dark'],
               ['Light','https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png','dark'],
               ['Street Map','https://tile.openstreetmap.org/{z}/{x}/{y}.png','dark']]

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
                    padding='20px',
                    transition='slide-right',
                    transitionDuration=300,
                    
                    children=[
                         html.Div(
                            className="content1",
                            children=[
                                html.H1('Dummy Block', className="title-block"),
                                html.H4('Summary'),
                                dmc.Spoiler(
                                    className='summary-content',
                                    showLabel='Show more',
                                    hideLabel='Hide',
                                    maxHeight=50,
                                    style={'marginBottom':35},
                                    children=[
                                        dmc.Text(
                                            '''
                                            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi luctus elit at eros accumsan iaculis. Nulla facilisi. Morbi vitae venenatis ante. Nulla dui tellus, euismod at malesuada ac, luctus quis orci. Nullam in eros mollis, vulputate neque ut, vulputate dolor. In sed ultrices mauris. Ut vitae dolor augue. Ut ac purus eu felis scelerisque facilisis. Donec consectetur odio orci, non volutpat eros suscipit vestibulum. Quisque a fermentum massa. Sed ac nibh nibh.
                                            '''
                                        )
                                    ]
                                )
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

                                        dmc.Button('View full details', id='PDF_Button',variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='material-symbols:picture-as-pdf-outline',width=25), 
                                        style={'marginTop':30, 'marginBottom':30})
                                ]),
                                value="info"),

                            dmc.TabsPanel(
                                html.Div(
                                    className="table2-content",
                                    children=[
                                        
                                        dmc.Accordion(
                                            value='map_filter_val',
                                            style={'marginTop':30},
                                            radius=10,
                                            children=[dmc.AccordionItem(
                                                [
                                                    dmc.AccordionControl('Map Settings', icon=DashIconify(icon='ic:twotone-map', width=25)),
                                                    dmc.AccordionPanel(
                                                        html.Div(
                                                            className='accordion-content',
                                                            children=[
                                                                html.H5('Layout map', style={'marginTop':10}),
                                                                dmc.RadioGroup(
                                                                    [dmc.Radio(i, value=k, color=c) for i, k, c in layout_data],
                                                                    id='map_layout',
                                                                    value='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                                                    orientation='vertical',
                                                                    spacing='xs',
                                                                    style={'marginBottom':20}
                                                                )
                                                            ]
                                                        )
                                                    )
                                                ],value='map_filter_val'
                                            )], variant='contained'
                                        ),
                                        
                                        dmc.Accordion(
                                            value='block_filter_val',
                                            style={'marginTop':10},
                                            radius=10,
                                            children=[dmc.AccordionItem(
                                                [
                                                    dmc.AccordionControl('Block Filter', icon=DashIconify(icon='mdi:surface-area',width=20)),
                                                    dmc.AccordionPanel(
                                                        html.Div(
                                                            className='accordion-content2',
                                                            children=[
                                                                html.H5('Block Name', style={'marginTop':10}),
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
                                                            className='accordion_content3',
                                                            children=[
                                                        html.H5('Well Name', style={'marginTop':10}),
                                                        dmc.MultiSelect(
                                                            placeholder="Select Borehole Name",
                                                            id="multiselect-borehole",
                                                            value=all_wells['Well_Name'].unique().tolist(),
                                                            data=all_wells['Well_Name'].unique().tolist(),
                                                            style={'marginTop':10},
                                                            clearable=True,
                                                            searchable=True,
                                                            nothingFound= 'No Options Found'
                                                            ),
                                                        
                                                        # html.H5('TVDSS in Meters', style={'marginTop':20}),
                                                        # dmc.RangeSlider(
                                                        #     id='range-slider-TVDSS',
                                                        #     value=[500,2000],
                                                        #     max=5000,
                                                        #     min=0,
                                                        #     marks=[
                                                        #         {'value':2000, 'label':'2000m'},
                                                        #         {'value':4000, 'label':'4000m'},
                                                        #         ],
                                                        #     style={'marginTop':10},
                                                        #     color='dark'),
                                                        # dmc.Text(id='output-porosity'), #output for slider porosity

                                                        html.H5('Wellbore Orientation', style={'marginTop':30}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_orientation_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Vertical',value='Vertical',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Horizontal',value='Horizontal',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Directional',value='Directional',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=['Vertical','Horizontal','Directional']
                                                        ),

                                                        html.H5('Status', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_status_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Active',value='Active',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Inactive',value='Inactive',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Shut-in',value='Shut-in',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Suspended',value='Suspended',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Abandoned',value='Abandoned',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=['Active','Inactive','Shut-in','Suspended','Abandoned']
                                                        ),

                                                        html.H5('Purpose', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_purpose_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Exploration',value='Exploration',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Production',value='Production',color='dark',style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Appraisal',value='Appraisal',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Injection',value='Injection',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Monitoring',value='Monitoring',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Abandonment',value='Abandonment',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=['Exploration','Production','Appraisal','Injection','Monitoring','Abandonment']
                                                        ),

                                                        html.H5('Type', style={'marginTop':20}),
                                                        dmc.CheckboxGroup(
                                                            id='checkbox_type_well',
                                                            orientation='vertical',
                                                            children=[
                                                                dmc.Checkbox(label='Oil',value='Oil',color='dark', style={'marginTop':0}),
                                                                dmc.Checkbox(label='Gas',value='Gas',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Water',value='Water',color='dark', style={'marginTop':-15}),
                                                                dmc.Checkbox(label='Observation',value='Observation',color='dark', style={'marginTop':-15})
                                                            ],
                                                            value=['Oil','Gas','Water','Observation']
                                                        ),
                                                        dmc.Button('Reset', id='reset_well', variant='outline', color='dark', radius='10px', leftIcon=DashIconify(icon='material-symbols:restart-alt', width=25), 
                                                                    style={'marginTop':'25px'})

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
                                        dmc.Paper(
                                            children=[
                                                html.H4('Block', style={'marginTop':5, 'paddingLeft':10}),
                                                html.P('A download section for block coordinates and information', style={'marginTop':5, 'marginLeft':10}),
                                                dmc.Button('Download data as CSV', id='CSV-button', variant='outline',color='dark',radius='10px', leftIcon=DashIconify(icon='ph:file-csv',width=25),style={'marginTop':25, 'marginLeft':10}),
                                                dcc.Download(id='download_csv_df'),
                                                html.Br(),
                                                dmc.Button('Download data as GeoJSON', id='GeoJSON-button',variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='mdi:code-json',width=25), style={'marginTop':10, 'marginLeft':10}),
                                                dcc.Download(id='download_geojson_df'),
                                                html.Br(),
                                                dmc.Button('Download data as SHP', id='SHP-button',variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='gis:shape-file',width=25), style={'marginTop':10,'marginBottom':10, 'marginLeft':10}),
                                                dcc.Download(id='download_shp_df')
                                                ],
                                            radius='10px',
                                            p='xs',
                                            withBorder=1,
                                            style={'marginTop':30}
                                            ),

                                        dmc.Paper(
                                            children=[
                                            html.H4('Well', style={'marginTop':5, 'marginLeft':10}),
                                            html.P('A download section for wellbore coordinates and information', style={'marginTop':5, 'marginLeft':10}),
                                            dmc.Button('Download data as CSV', id='CSV-button2', variant='outline',color='dark',radius='10px', leftIcon=DashIconify(icon='ph:file-csv',width=25),style={'marginTop':25, 'marginLeft':10}),
                                            dcc.Download(id='download_csv_df2'),
                                            html.Br(),
                                            dmc.Button('Download data as GeoJSON', id='GeoJSON-button2',variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='mdi:code-json',width=25), style={'marginTop':10, 'marginLeft':10}),
                                            dcc.Download(id='download_geojson_df2'),
                                            html.Br(),
                                            dmc.Button('Download data as SHP', id='SHP-button2',variant='outline',color='dark',radius='10px',leftIcon=DashIconify(icon='gis:shape-file',width=25), style={'marginTop':10, 'marginBottom':10, 'marginLeft':10}),
                                            dcc.Download(id='download_shp_df2'),
                                            ],
                                            radius='10px',
                                            p='xs',
                                            withBorder=1,
                                            style={'marginTop':10, 'marginBottom':30}
                                        )
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
    Output('multiselect-borehole','data'),
    Input('checkbox_orientation_well','value'),
    Input('checkbox_status_well','value'),
    Input('checkbox_purpose_well','value'),
    Input('checkbox_type_well','value')
)

def set_well_option(chosen_orientation, chosen_status, chosen_purpose, chosen_type):
    df_well = all_wells[(all_wells['Well_Orientation'].isin(chosen_orientation)) & (all_wells['Well_Status'].isin(chosen_status)) & (all_wells['Well_Purpose'].isin(chosen_purpose)) & (all_wells['Well_Type'].isin(chosen_type))]
    return pd.unique(df_well['Well_Name'].to_list())

@app.callback(
    Output('multiselect-block','value'),
    Output('num-wells','value'),
    Output('km-slider','value'),
    Output('range-slider-reserve','value'),
    Output('checkbox_status_block','value'),
    Output('multiselect-operator','value'),
    Input('reset-block','n_clicks')
)

def reset_filter_block(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        reset_df = all_blocks[(all_blocks['num_wells'].between(all_blocks['num_wells'].min(), all_blocks['num_wells'].max())) & (all_blocks['sq_km'].between(all_blocks['sq_km'].min(), all_blocks['sq_km'].max())) & (all_blocks['est_reserve'].between(all_blocks['est_reserve'].min(), all_blocks['est_reserve'].max())) & (all_blocks['Status'].isin(all_blocks['Status'])) & (all_blocks['Operator'].isin(all_blocks['Operator']))]
        reset_block_name = pd.unique(reset_df['Block_Name'].to_list())
        reset_num_blocks = reset_df['num_wells'].min(), reset_df['num_wells'].max()
        reset_km_blocks = reset_df['sq_km'].min(), reset_df['sq_km'].max()
        reset_reserve_blocks = reset_df['est_reserve'].min(), reset_df['est_reserve'].max()
        reset_status_blocks = ['Exploration','Development','Production','Abandoned']
        reset_operator_blocks = pd.unique(reset_df['Operator'].to_list())
        
        return reset_block_name, reset_num_blocks, reset_km_blocks, reset_reserve_blocks, reset_status_blocks, reset_operator_blocks

@app.callback(
    Output('multiselect-borehole','value'),
    Output('checkbox_orientation_well','value'),
    Output('checkbox_status_well','value'),
    Output('checkbox_purpose_well','value'),
    Output('checkbox_type_well','value'),
    Input('reset_well','n_clicks')
)

def reset_filter_well(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        reset_df = all_wells[(all_wells['Well_Orientation'].isin(all_wells['Well_Orientation'])) & (all_wells['Well_Status'].isin(all_wells['Well_Status'])) & (all_wells['Well_Purpose'].isin(all_wells['Well_Purpose'])) & (all_wells['Well_Type'].isin(all_wells['Well_Type']))]
        reset_well_name = pd.unique(reset_df['Well_Name'].to_list())
        reset_orient = ['Vertical', 'Horizontal', 'Directional']
        reset_status = ['Active', 'Inactive','Shut-in','Suspended','Abandoned']
        reset_purpose = ['Exploration','Production','Appraisal','Injection','Monitoring','Abandonment']
        reset_type = ['Oil','Gas','Water','Observation']
        
        return reset_well_name, reset_orient, reset_status, reset_purpose, reset_type

@app.callback(
    Output('output-map','children'),
    Input('multiselect-block','value'),
    Input('multiselect-block','data'),
    Input('multiselect-borehole','value'),
    Input('multiselect-borehole','data'),
    Input('map_layout','value')
)

def plot_map(block_submitted_value, block_submitted_data, well_submitted_value, well_submitted_data, layout_map):
    edited_layer= all_blocks[(all_blocks['Block_Name'].isin(block_submitted_value)) & (all_blocks['Block_Name'].isin(block_submitted_data))]
    edited_point = all_wells[(all_wells['Well_Name'].isin(well_submitted_value)) & (all_wells['Well_Name'].isin(well_submitted_data))]
    
    layer_blocks = dl.GeoJSON(id='block_load',
                            data=json.loads(edited_layer.to_json()),
                            hoverStyle=arrow_function(dict(weight=5, fillColor='#45b6fe', fillOpacity=0.5, color='black', dashArray='')),
                            options=dict(style={
                                                'color':'black',
                                                'weight':3,
                                                'dashArray':'30 10',
                                                'dashOffset':'5',
                                                'opacity':1,
                                                'fillColor':'#3a9bdc'
                                                }))
    bounds = edited_layer.total_bounds
    x = mean([bounds[0], bounds[2]])
    y = mean([bounds[1], bounds[3]])
    location = (y, x)
    
    layer_well = dl.GeoJSON(id='point_load',
                            data=json.loads(edited_point.to_json()))
    bounds_point = edited_point.total_bounds
    x_point = mean([bounds_point[0], bounds_point[2]])
    y_point = mean([bounds_point[1], bounds_point[3]])
    location_point = (y_point, x_point)
    
    if edited_layer.empty and edited_point.empty:
        # Generate map without polygons and points
        return dl.Map(children=[dl.TileLayer(url=layout_map),
                        dl.GestureHandling(),
                        dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares",
                                        activeColor="#C29200", completedColor="#972158")],
                        center=[5.3, 96.3],
                        zoom=11,
                        style={
                            'z-index':'0',
                            'width': '1750px',
                            'height': '965px',
                            'marginLeft':'20px',
                        })
    elif edited_layer.empty:
        #Generate map without polygons
        return dl.Map(children=[dl.GeoJSON(layer_well),
                        dl.TileLayer(url=layout_map),
                        dl.GestureHandling(),
                        dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares",
                                        activeColor="#C29200", completedColor="#972158")],
                        center=[y_point, x_point],
                        zoom=11,
                        style={
                                'z-index':'0',
                                'width': '1750px',
                                'height': '965px',
                                'marginLeft':'20px',
                        })
    elif edited_point.empty:
        #Generate map without points
        return dl.Map(children=[dl.GeoJSON(layer_blocks, id='layer_blocks'),
                        dl.TileLayer(url=layout_map),
                        dl.GestureHandling(),
                        dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares",
                                        activeColor="#C29200", completedColor="#972158")],
                        center=[y, x],
                        zoom=11,
                        style={
                            'z-index':'0',
                            'width': '99%',
                            'height': '965px',
                            'marginLeft':'20px',
                            'float':'right'
                        })
        
    return dl.Map(children=[dl.GeoJSON(layer_blocks, id='layer_blocks'),
                    dl.GeoJSON(layer_well),
                    dl.TileLayer(url=layout_map),
                    dl.GestureHandling(),
                    dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares",
                                    activeColor="#C29200", completedColor="#972158")],
                    center=[y, x],
                    zoom=11,
                    style={
                        'z-index':'0',
                        'width': '99%',
                        'height': '965px',
                        'marginLeft':'20px',
                        'float':'right'
                    })
    
# Create the download buttons for block datasets

@app.callback(
    Output('download_csv_df', 'data'),
    Input('CSV-button', 'n_clicks'),
    prevent_initial_call=True
)

def generate_csv(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return dcc.send_data_frame(all_blocks.to_csv, "MyCSV_Blocks.csv")

@app.callback(
    Output('download_geojson_df','data'),
    Input('GeoJSON-button','n_clicks'),
    prevent_initial_call=True
)
def generate_geojson(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # Read the generated JSON file and send it as bytes
        with open('GeoJSON files/blocks.geojson', 'r') as file:
            data = file.read()
        return dcc.send_bytes(data.encode(), "MyGeoJSON_Blocks.json")

@app.callback(
    Output('download_shp_df','data'),
    Input('SHP-button','n_clicks'),
    prevent_initial_call=True
)

def generate_shp(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # Read the generated Shapefile and send it as bytes
        with open('SHP zipfile/all_blocks.zip', 'rb') as file:
            data = file.read()
        return dcc.send_bytes(data, "MySHP_Blocks.zip")

#create the download button for well datasets

@app.callback(
    Output('download_csv_df2', 'data'),
    Input('CSV-button2', 'n_clicks'),
    prevent_initial_call=True
)

def generate_csv(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return dcc.send_data_frame(all_wells.to_csv, "MyCSV_Wells.csv")

@app.callback(
    Output('download_geojson_df2','data'),
    Input('GeoJSON-button2','n_clicks'),
    prevent_initial_call=True
)
def generate_geojson(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # Read the generated JSON file and send it as bytes
        with open('GeoJSON files/wells.geojson', 'r') as file:
            data = file.read()
        return dcc.send_bytes(data.encode(), "MyGeoJSON_Wells.json")

@app.callback(
    Output('download_shp_df2','data'),
    Input('SHP-button2','n_clicks'),
    prevent_initial_call=True
)

def generate_shp(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # Read the generated Shapefile and send it as bytes
        with open('SHP zipfile/wells.zip', 'rb') as file:
            data = file.read()
        return dcc.send_bytes(data, "MySHP_Wells.zip")


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