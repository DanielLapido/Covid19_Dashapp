import dash
import dash_bootstrap_components as dbc  # import the library
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

import pandas as pd
import time
import numpy as np
import json

# Read data
Confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
Deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")


report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")
report.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', "Confirmed", "Deaths"]

report.loc[:, "Confirmed"] = report.loc[:, "Confirmed"].fillna(0)
date = pd.to_datetime(Confirmed.columns[4:-1])

conf2 = pd.melt(Confirmed, id_vars=Confirmed.columns[0:4])
# dates = pd.to_datetime(conf2.variable)
# conf2.variable = dates

deaths2 = pd.melt(Deaths, id_vars=Deaths.columns[0:4])

globalreport = pd.concat([conf2, deaths2.value], axis=1)
globalreport.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', 'Date', 'Confirmed', 'Deaths']

globalreport['Country/Region'] = pd.Categorical(globalreport['Country/Region'])
# print(globalreport.dtypes)

factors = sorted(globalreport['Country/Region'].unique())




import pandas as pd
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

import plotly.express as px

bubble = np.log2(report.Confirmed + 1)
fig = px.scatter_mapbox(report, lat="Lat", lon="Long", hover_name="Province/State", hover_data=["Country/Region", "Confirmed"],
                        color_discrete_sequence=["fuchsia"], zoom=1.5, height=800, size=bubble)
fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

import plotly.graph_objects as go # or plotly.express as px
# fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
# fig.add_trace( ... )
# fig.update_layout( ... )

fig2 = px.scatter_geo(report, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble, height=800, projection="orthographic")

bubble2 = np.log2(globalreport.Confirmed + 1)
fig3 = px.scatter_geo(globalreport, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble2, height=800,
                     animation_frame="Date",
                     projection="natural earth")


app = dash.Dash()
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Tab one', children=[
            dcc.Graph(
                figure=fig
            )
        ]),
        dcc.Tab(label='Tab two', children=[
            dcc.Graph(
                figure=fig2
            )
        ]),
        dcc.Tab(label='Tab three', children=[
            dcc.Graph(
                figure=fig3
            )
        ]),
    ])
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

