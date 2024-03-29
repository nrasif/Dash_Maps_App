import dash
from dash import Dash, html, dcc, ctx, State
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
import time

import geopandas as gpd

# --------------------Chat Bot-------------------------

import nltk
from nltk.stem import WordNetLemmatizer
import pickle
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
model = load_model('chatbot_model/chatbot.h5')

import random
intents = json.loads(open('chatbot_model/data.json').read())
words = pickle.load(open('chatbot_model/words.pkl','rb'))
classes = pickle.load(open('chatbot_model/classes.pkl','rb'))

def clean_up_sentence(sentence):

    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):

    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)

    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words) 
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
               
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
   
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    error = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>error]
    
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# function to get the response from the model
def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

# function to predict the class and get the response
def chatbot_response(text):
    ints = predict_class(text, model)
    res = getResponse(ints, intents)
    return res



# --------------------Chat Bot-------------------------

all_blocks = gpd.read_file('GeoJSON Files/blocks.geojson')
all_wells = gpd.read_file('GeoJSON Files/wells.geojson')

all_blocks_download = all_blocks.copy()
all_wells_download = all_wells.copy()

all_blocks['tooltip'] = all_blocks['name']
all_blocks['popup'] = '''


<strong><H4 style="margin-top:10px; margin-bottom:20px; font-family:Ubuntu, sans-serif; font-size: 25px; color:#3F72AF;">
''' + all_blocks['name'] + '</H4></strong>' + """


<table style="height: 50px; width: 250px;">
    <tbody>
    <tr>
    <th class="data-cell-left"><strong>Status</strong></th>
    <td class="data-cell-right"> """ + all_blocks['status'] + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Operator</strong></th>
    <td class="data-cell-right"> """ + all_blocks['operator'] + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Number of Wells</strong></th>
    <td class="data-cell-right"> """ + all_blocks['num_well'].map(str) + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Area</strong></th>
    <td class="data-cell-right"> """ + all_blocks['sq_km'].map(str) + """ km<sup>2</sup></td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Reserve Estimation</strong></th>
    <td class="data-cell-right"> """ + all_blocks['reserve'].map(str) + """ MMbbl</td>
    </tr>
    """


all_wells['tooltip'] = all_wells['name']
all_wells['popup'] = '''


<strong><H4 style="margin-top:10px; margin-bottom:20px; font-family:Ubuntu, sans-serif; font-size: 25px; color:#3F72AF;">
''' + all_wells['name'] + '</H4></strong>' + """


<table style="height: 50px; width: 250px;">
    <tbody>
    <tr>
    <th class="data-cell-left"><strong>Orientation</strong></th>
    <td class="data-cell-right"> """ + all_wells['orient'] + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Status</strong></th>
    <td class="data-cell-right"> """ + all_wells['status'] + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Purpose</strong></th>
    <td class="data-cell-right"> """ + all_wells['purpose'] + """</td>
    </tr>
    <tr>
    <th class="data-cell-left"><strong>Area</strong></th>
    <td class="data-cell-right"> """ + all_wells['type'] + """</td>
    </tr>
    """

# Write the data to a Shapefile
def shp_writer(data, path):
    return data.to_file(driver='ESRI Shapefile', filename=path)

shp_writer(all_blocks_download, 'SHP files/all_blocks/all_blocks.shp')
shp_writer(all_wells_download, 'SHP files/all_wells/all_wells.shp')

# Create a ZIP file containing all the Shapefile files
def zip_shp(path_zip, data_shp):
    with zipfile.ZipFile(path_zip, 'w') as zip:
        for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg']:
            filename = data_shp.format(ext)
            if os.path.exists(filename):
                zip.write(filename)

zip_shp(path_zip='SHP zipfile/blocks.zip', data_shp='SHP files/all_blocks/all_blocks{}')
zip_shp(path_zip='SHP zipfile/wells.zip', data_shp='SHP files/all_wells/all_wells{}')



layout_data = [['Satellite','https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}','dark'],
               ['Dark','https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png','dark'],
               ['Light','https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png','dark'],
               ['Street Map','https://tile.openstreetmap.org/{z}/{x}/{y}.png','dark']]

#----------------------------Dash Apps----------------------------------------

app = Dash(__name__, suppress_callback_exceptions=True, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

conv_hist=[]

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
                                                                    value=all_blocks['name'].unique().tolist(),
                                                                    data=all_blocks['name'].unique().tolist(),
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
                                                                    value=all_blocks['operator'].unique().tolist(),
                                                                    data=all_blocks['operator'].unique().tolist(),
                                                                    style={'marginTop':10},
                                                                    clearable=True,
                                                                    searchable=True,
                                                                    nothingFound= 'No Options Found'
                                                                    ),

                                                                html.H5('Number of Wells', style={'marginTop':20}),
                                                                dmc.RangeSlider(
                                                                    id='num-wells',
                                                                    value=[all_blocks['num_well'].min(), all_blocks['num_well'].max()],
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
                                                                    value=[all_blocks['reserve'].min(), all_blocks['reserve'].max()],
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
                                                            value=all_wells['name'].unique().tolist(),
                                                            data=all_wells['name'].unique().tolist(),
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
                                                html.H4('Block Dataset', style={'marginTop':5, 'paddingLeft':10}),
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
                                            html.H4('Well Dataset', style={'marginTop':5, 'marginLeft':10}),
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
        className='chatbot',
        children=[
            dmc.Accordion(
                value='chatbot',
                radius=10,
                children=[
                    dmc.AccordionItem(
                        [
                            dmc.AccordionControl('Waviv MiniBot', icon=DashIconify(icon='lucide:bot', width=25)),
                            dmc.AccordionPanel(
                                html.Div(
                                    children = [
                                        html.Div(className='div-chatbot', children=[
                                            dmc.LoadingOverlay(
                                                html.Div(id='response-chatbot'),
                                                 loaderProps={"variant": "dots", "color": "dark", "size": "xl"},
                                                 overlayBlur=2,
                                                 overlayColor='#F8F9FA', style={'height':'500px'}
                                                 )]),
                                        dmc.Textarea(
                                        placeholder='Send a message...',
                                        id='input-msg',
                                        style={'width':400, 'border': '2px solid #909090', 'border-radius':'5px'},
                                        variant='filled',
                                        autosize=True,
                                        minRows=2,
                                        maxRows=4
                                        ),
                                        dmc.ActionIcon(DashIconify(icon="ri:send-plane-fill", width=20), size=34, \
                                            variant="outline", id='submit-msg', color='gray', n_clicks=0, style={'position':'absolute',
                                                                                                                 'right':'40px',
                                                                                                                 'bottom':'52px'}),
                                        dmc.ActionIcon(DashIconify(icon='codicon:debug-restart', width=20), size=34, \
                                            variant="outline", id='reset-msg', color='gray', n_clicks=0, style={'position':'absolute',
                                                                                                                'right':'40px',
                                                                                                                'bottom':'16px'})
                                    ]
                                ),
                            )
                        ], value='chatbot'
                    )
                ], variant='contained'
            )
        ]
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
    df_block = all_blocks[(all_blocks['num_well'].between(chosen_numwell[0], chosen_numwell[1])) & (all_blocks['sq_km'].between(chosen_km[0], chosen_km[1])) & (all_blocks['reserve'].between(chosen_reserve[0], chosen_reserve[1])) & (all_blocks['status'].isin(chosen_status)) & (all_blocks['operator'].isin(chosen_operator))]
    return pd.unique(df_block['name'].to_list())

@app.callback(
    Output('multiselect-borehole','data'),
    Input('checkbox_orientation_well','value'),
    Input('checkbox_status_well','value'),
    Input('checkbox_purpose_well','value'),
    Input('checkbox_type_well','value')
)

def set_well_option(chosen_orientation, chosen_status, chosen_purpose, chosen_type):
    df_well = all_wells[(all_wells['orient'].isin(chosen_orientation)) & (all_wells['status'].isin(chosen_status)) & (all_wells['purpose'].isin(chosen_purpose)) & (all_wells['type'].isin(chosen_type))]
    return pd.unique(df_well['name'].to_list())

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
        reset_df = all_blocks[(all_blocks['num_well'].between(all_blocks['num_well'].min(), all_blocks['num_well'].max())) & (all_blocks['sq_km'].between(all_blocks['sq_km'].min(), all_blocks['sq_km'].max())) & (all_blocks['reserve'].between(all_blocks['reserve'].min(), all_blocks['reserve'].max())) & (all_blocks['status'].isin(all_blocks['status'])) & (all_blocks['operator'].isin(all_blocks['operator']))]
        reset_block_name = pd.unique(reset_df['name'].to_list())
        reset_num_blocks = reset_df['num_well'].min(), reset_df['num_well'].max()
        reset_km_blocks = reset_df['sq_km'].min(), reset_df['sq_km'].max()
        reset_reserve_blocks = reset_df['reserve'].min(), reset_df['reserve'].max()
        reset_status_blocks = ['Exploration','Development','Production','Abandoned']
        reset_operator_blocks = pd.unique(reset_df['operator'].to_list())
        
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
        reset_df = all_wells[(all_wells['orient'].isin(all_wells['orient'])) & (all_wells['status'].isin(all_wells['status'])) & (all_wells['purpose'].isin(all_wells['purpose'])) & (all_wells['type'].isin(all_wells['type']))]
        reset_well_name = pd.unique(reset_df['name'].to_list())
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
    edited_layer= all_blocks[(all_blocks['name'].isin(block_submitted_value)) & (all_blocks['name'].isin(block_submitted_data))]
    edited_point = all_wells[(all_wells['name'].isin(well_submitted_value)) & (all_wells['name'].isin(well_submitted_data))]
    
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
        return dl.Map(children=[dl.TileLayer(url=layout_map, attribution = '&copy; <a href="http://www.waviv.com/">Waviv Technologies</a> '),
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
                        dl.TileLayer(url=layout_map, attribution = '&copy; <a href="http://www.waviv.com/">Waviv Technologies</a> '),
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
                        dl.TileLayer(url=layout_map, attribution = '&copy; <a href="http://www.waviv.com/">Waviv Technologies</a> '),
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
                    dl.TileLayer(url=layout_map, attribution = '&copy; <a href="http://www.waviv.com/">Waviv Technologies</a> '),
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
        return dcc.send_data_frame(all_blocks_download.to_csv, "MyCSV_Blocks.csv")

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
        return dcc.send_data_frame(all_wells_download.to_csv, "MyCSV_Wells.csv")

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
        with open('GeoJSON files/wells.geojson', 'rb') as file:
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
    Output('response-chatbot','children'),
    Input('submit-msg','n_clicks'),
    Input('reset-msg','n_clicks'),
    State('input-msg','value')
)

def update_convo(click1, click2, text):
    
    button_click = ctx.triggered_id
    
    global conv_hist
    
    if button_click == 'submit-msg':
        time.sleep(1)
        
        response = chatbot_response(text)
        
        whole_div = html.Div(children=[
            dmc.Grid(gutter='xs',children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=20), color='gray', radius='xl', size='sm', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
                                               dmc.Col(html.Div(html.H5(text,style={'text-align':'left'})), className='grid-chat')]),
            dmc.Grid(gutter='xs',children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="lucide:bot", width=15), color='blue', radius='xl', size='sm', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
                                               dmc.Col(html.Div(html.H5(response,style={'text-align':'left'})), className='grid-chat')])
        ])
        # rcvd = [dmc.Grid(gutter='xs',children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=20), color='gray', radius='xl', size='sm', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
        #                                        dmc.Col(html.Div(html.H5(text,style={'text-align':'left'})), className='grid-chat')])]
        # rspd = [dmc.Grid(gutter='xs',children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="lucide:bot", width=15), color='blue', radius='xl', size='sm', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
        #                                        dmc.Col(html.Div(html.H5(response,style={'text-align':'left'})), className='grid-chat')])]
        
        conv_hist.append(whole_div)
        
        return conv_hist
    
    elif button_click == 'reset-msg':
        time.sleep(1)
        conv_hist = []
        clean_comp = [html.H5('Message is clear', className='default_chat')]
        return clean_comp
    
    else:
        default_comp = [html.H5('Say Hi to our little staff here, a Waviv MiniBot!', className='default_chat'),
                        html.H5('pssstt... he knows everything about this dashboard', style={'text-align':'center','width':'400px'})]
        return default_comp

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
    app.run_server(debug=True, port = 8000)