import dash
import dash_html_components as html
import dash_core_components as dcc
import dash
import dash_bootstrap_components as dbc  # import the library
import dash_core_components as dcc
import dash_html_components as html
import folium
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import json
from textwrap import dedent as d
import pandas as pd
import time
import numpy as np


# Read data
Confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Confirmed_archived_0325.csv")
Deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Deaths_archived_0325.csv")
Recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/archived_data/archived_time_series/time_series_19-covid-Recovered_archived_0325.csv")

report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1], Recovered.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")

report.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', "Confirmed", "Deaths", "Recovered"]

report.loc[:, "Confirmed"] = report.loc[:, "Confirmed"].fillna(0)
date = pd.to_datetime(Confirmed.columns[4:-1])

conf2 = pd.melt(Confirmed, id_vars=Confirmed.columns[0:4])
dates = pd.to_datetime(conf2.variable)
conf2.variable = dates

deaths2 = pd.melt(Deaths, id_vars=Deaths.columns[0:4])
recovered2 = pd.melt(Recovered, id_vars=Recovered.columns[0:4])

globalreport = pd.concat([conf2, deaths2.value, recovered2.value], axis=1)
globalreport.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', 'Date', 'Confirmed', 'Deaths', 'Recovered']

globalreport['Country/Region'] = pd.Categorical(globalreport['Country/Region'])
# print(globalreport.dtypes)

factors = sorted(globalreport['Country/Region'].unique())




import pandas as pd
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

import plotly.express as px

# fig = px.scatter_mapbox(report, lat="Lat", lon="Long", hover_name="Province/State", hover_data=["Country/Region", "Confirmed"],
#                         color_discrete_sequence=["fuchsia"], zoom=1, height=800)

bubble = np.log2(report.Confirmed + 1)

fig = px.scatter_geo(report, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble, height=800, projection="orthographic")

fig2 = px.scatter_geo(report, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble, height=800)

fig3 = px.scatter_geo(report, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble, height=400, projection="orthographic")

m = folium.Map(location=[0, 0], tiles='cartodbpositron',
               min_zoom=1, max_zoom=4, zoom_start=1)

for i in range(0, len(report)):
    folium.Circle(
        location=[report.iloc[i]['Lat'], report.iloc[i]['Long']],
        color='crimson',
        tooltip='<li><bold>Country : '+str(report.iloc[i]['Country/Region'])+
                    '<li><bold>Province : '+str(report.iloc[i]['Province/State'])+
                    '<li><bold>Confirmed : '+str(report.iloc[i]['Confirmed'])+
                    '<li><bold>Deaths : '+str(report.iloc[i]['Deaths'])+
                    '<li><bold>Recovered : '+str(report.iloc[i]['Recovered']),
        radius=int(report.iloc[i]['Confirmed'])**1.1).add_to(m)


m.save('map.html')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
            html.Iframe(id="map", srcDoc=open('map.html', 'r').read(), width='100%', height='300px')
        ]),
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)

