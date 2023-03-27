import dash
import dash_leaflet as dl

app = dash.Dash()

geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [2.3199, 48.8499],
                    [2.3215, 48.8595],
                    [2.3293, 48.8566],
                    [2.3274, 48.8464],
                    [2.3199, 48.8499]
                ]]
            }
        }
    ]
}

style = {
    "color": "black",
    "dashArray": "5, 5",
    "fillColor": "blue",
    "fillOpacity": 0.4,
}

geojson = dl.GeoJSON(
    data=geojson_data,
    id="geojson",
    options=style
)

app.layout = dl.Map(center=[48.85, 2.32], zoom=13, children=[geojson])

if __name__ == "__main__":
    app.run_server()