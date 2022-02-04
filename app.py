# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import shapely.geometry
from dash import dcc, html
from dash.dependencies import Input, Output

token = open(".mapbox_token").read()

px.set_mapbox_access_token(token)

app = dash.Dash(__name__)



print("Reading Files")
homes = pd.read_csv('./data/affordable_housing_geocoded.csv')

libraries = gpd.read_file('./data/libraries_datasd.geojson')

mosques = pd.read_csv('./data/san_diego_mosques_geocoded.csv')
recs = gpd.read_file('./data/rec_centers_datasd.geojson')
transit_stops = gpd.read_file('./data/transit_stops_datasd.geojson')

lats = []
lons = []

t = [0,2]
routes = gpd.read_file('./data/transit_routes_datasd.geojson').query('route_type in @t')

for feature in routes.geometry:
    if isinstance(feature, shapely.geometry.linestring.LineString):
        linestrings = [feature]
    elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
        linestrings = feature.geoms
    else:
        continue

    for linestring in linestrings:
        x, y = linestring.xy
        lats = np.append(lats, y)
        lons = np.append(lons, x)
        lats = np.append(lats, None)
        lons = np.append(lons, None)




print("plotting data")
fig = px.scatter_mapbox(homes, lat='lat', lon='lon', hover_data=['Bedrooms'] , hover_name='Apartment', zoom=10   ,)
app.layout = html.Div(children=[
    html.H1(children='Sunny San Diego'),

    dcc.Graph(
        id='san-diego-map',
        figure=fig,
        style={ 'height': 550, 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}
    ),
    # html.Br(),
    html.Label('Select Amenity'),
        dcc.Checklist(
            id = 'checkbox-list',
            options=[
                {'label': 'Libraries', 'value': 'Libraries'},
                {'label': 'Train', 'value': 'Train'},
                {'label': 'Mosques', 'value': 'Mosques'},
                {'label': 'Recreation Centers', 'value': 'Recreation Centers'},
                {'label': 'Transit Stops', 'value': 'Transit Stops'},
            ],
            value=[],
        ),
        html.Button("Reset", id="reset-button", n_clicks=0),

    
]
)

@app.callback(
    Output('san-diego-map', 'figure'),
    
    Input('checkbox-list', 'value'),
    # Input("reset-button", "n_clicks")
    
)
def update_map(value):

    if 'Libraries' in value:
        fig.add_trace(px.scatter_mapbox(libraries, lat='lat', lon='lng', hover_name='name',  opacity=0.5,color_discrete_sequence=['purple']).data[0])
    if 'Train' in value:
        fig.add_trace(px.line_mapbox(lat=lats, lon=lons, color_discrete_sequence=['black']).data[0])
    if 'Mosques' in value:
        fig.add_trace(px.scatter_mapbox(mosques, lat='lat', lon='lon', hover_name='Name', color_discrete_sequence=['red']).data[0])
    if 'Recreation Centers' in value:
        fig.add_trace(px.scatter_mapbox(recs, lat='lat', lon='lng', hover_name='park_name',  color_discrete_sequence=['green']).data[0])
    if 'Transit Stops' in value:
        fig.add_trace(px.scatter_mapbox(transit_stops, lat='lat', lon='lng', hover_name='stop_name', color_discrete_sequence=['orange']).data[0])

    return fig

# @app.callback(
#     Output("san-diego-map", "figure"),
#     Input("reset-button", "n_clicks")
# )
# def reset_checklist(n_clicks):
#     if not n_clicks:
#         raise dash.exceptions.PreventUpdate
#     fig = px.scatter_mapbox(homes, lat='lat', lon='lon', hover_data=['Bedrooms'] , hover_name='Apartment', zoom=10   ,)

#     return fig


if __name__ == '__main__':
    app.run_server(debug=True)
