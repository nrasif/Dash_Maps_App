import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
import dash_leaflet as dl

from dash_extensions.javascript import arrow_function

import geopandas as gpd
import json
from statistics import mean

all_blocks = gpd.read_file('GeoJSON Files/blocks.geojson')

# -------------------------------------Dash Apps----------------------------------------

app = Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

app.layout = html.Section([
    html.Div(children=[
        html.H5('Block Name'),
        dmc.MultiSelect(
            placeholder="Select Block Name",
            id="multiselect-block",
            value=all_blocks['Block_Name'].unique().tolist(),
            data=all_blocks['Block_Name'].unique().tolist(),
            style={'marginTop':10},
            clearable=True,
            searchable=True,
            nothingFound= 'No Options Found'
            )
    ]),
    
    html.Div(id='output-map')
    ])

@app.callback(
    Output('output-map','children'),
    Input('multiselect-block','value'),
    Input('multiselect-block','data')
)

def plot_map(block_submitted_value, block_submitted_data):
    edited_layer= all_blocks[(all_blocks['Block_Name'].isin(block_submitted_value)) & (all_blocks['Block_Name'].isin(block_submitted_data))]
    
    #defining dl.GeoJSON for filtered edited_layer
    layer_blocks = dl.GeoJSON(id='block_load',
                            data=json.loads(edited_layer.to_json()),
                            hoverStyle=arrow_function(dict(weight=6, fillColor='#45b6fe', fillOpacity=0.5)),
                            options=dict(style={'color':'#3a9bdc',
                                        'weight':2,
                                        'dashArray':'30, 10',
                                        'dashOffset':'1',
                                        'opacity':1,
                                        }))
    bounds = edited_layer.total_bounds
    x = mean([bounds[0], bounds[2]])
    y = mean([bounds[1], bounds[3]])
    location = (y, x)
    
    if edited_layer.empty:
        return dl.Map(children=[dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
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

    return dl.Map(children=[dl.GeoJSON(layer_blocks),
                dl.TileLayer('url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
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

if __name__ == '__main__':
    app.run_server(debug=True, port = 8400)