#!-*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State, Event
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
import plotly
import json
import utils as ut

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

mapbox_access_token = "pk.eyJ1Ijoicm9ja3Nwb3JlIiwiYSI6ImNqbXhuZzRmdDN2OWcza255NzdhYXF5Y2IifQ.hSASwA7Z_wwCg7P0ib8lww"

DF_ITEMS = pd.DataFrame({
    'Items': ['', '', '', '', '', '']
})

DF_SITES = pd.DataFrame({
    'Stores': ['', '', '', '', '', ''],
    'Distances (miles)': ['', '', '', '', '', '']
})

data = [
    go.Scattermapbox(
        lat = ['33.746026'],
        lon = ['-84.390658'],
        mode = 'markers',
        marker = dict(
            size = 10,
            color = 'rgb(200, 0, 0)'
        ),
        text = ['Downtown Atlanta']
    )
]

sites = {}
distances = []

layout = go.Layout(
    autosize = True,
    hovermode = 'closest',
    mapbox = dict(
        accesstoken = mapbox_access_token,
        bearing = 0,
        center = dict(
            lat = 33.746026,
            lon = -84.390658
        ),
        pitch = 0,
        zoom = 12
    ),
)

fig1 = dict(data = data, layout = layout)

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
#app = dash.Dash(__name__)

app.config.supress_callback_exceptions = True

app.layout = html.Div(children = [
    html.H1(children = 'GroceryGo'),
    html.Div([

        html.H3(children = 'Fill your shopping list at the left'),
        html.Div([
            dt.DataTable(
                rows = DF_ITEMS.to_dict('records'),

                # optional - sets the order of columns
                columns = sorted(DF_ITEMS.columns),

                row_selectable = True,
                sortable = True,
                selected_row_indices = [],
                id = 'shoplist_table',
                editable = True
            ),
            ], style = {'width': '29%', 'display': 'inline-block'}),

        html.Div([
            dt.DataTable(
                rows = DF_SITES.to_dict('records'),

                # optional - sets the order of columns
                #columns=sorted(DF_SITES.columns, reverse = True),

                sortable = True,
                selected_row_indices = [],
                id = 'search_results',
                editable = True
            ),
            ], style = {'width': '29%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.H3(children = 'Enter your location'),
        dcc.Input(id = 'input_location', type = 'text', value = '33.746026,-84.390658'),
        html.Button(id = 'submit_button', type = 'submit', children = 'Search'),
        html.Div(id = 'output1')
    ]),

    html.Div([
        html.H3(children = 'Locations on the map (latitude,longitude)'),
        dcc.Graph(
            id = 'scatter_map',
            figure = fig1
            )
        ], style = {"height" : "60%", "width" : "100%", 'display': 'inline-block'})
])

@app.callback(Output('scatter_map', 'figure'),
              [],
              [State('shoplist_table', 'rows'),
               State('shoplist_table', 'selected_row_indices'),
               State('input_location', 'value')],
              [Event('submit_button', 'click')])
def update_dt(rows, selected_row_indices, value):
    global sites
    global data
    global distances
    distances = []
    grocery_list = [rows[id]['Items'] for id in selected_row_indices]
    lat, lon = value.split(',')
    lat = float(lat)
    lon = float(lon)
    sites = ut.get_sites(lat, lon, grocery_list)
    lat_list = []
    lon_list = []
    for key, value in sites.items():
        #print(value)
        lat_list.append(value[0])
        lon_list.append(value[1])
        distances.append(ut.distanceCalculator(lat, lon, value[0], value[1]))
    if len(lat_list) > 0:
        data = [
            go.Scattermapbox(
                lat = lat_list,
                lon = lon_list,
                mode = 'markers',
                marker = dict(
                    size = 10,
                    color = 'rgb(200, 0, 0)'
                ),
            ),
            go.Scattermapbox(
                lat = [lat],
                lon = [lon],
                mode = 'markers',
                marker = dict(
                    size = 10
                ),
                text = ['Your location'],
            )
        ]
    else:
        data = [
            go.Scattermapbox(
                lat = [lat],
                lon = [lon],
                mode = 'markers',
                marker = dict(
                    size = 10
                ),
                text = ['Your location'],
            )
        ]
    return dict(data = data, layout = layout)

@app.callback(Output('search_results', 'rows'),
              [Input('scatter_map', 'figure')])
def update_df(figure):
    print(distances)
    df_sites = pd.DataFrame({
        'Stores': [s[2] for k, s in sites.items()],
        'Distances (miles)': distances
    })
    return df_sites.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug = True)
