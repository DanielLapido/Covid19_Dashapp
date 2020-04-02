import dash
import dash_bootstrap_components as dbc  # import the library
import dash_core_components as dcc
import dash_html_components as html
import dash_admin_components as dac
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash

import pandas as pd
import time
import numpy as np
import json

# css_style = {
#     "title": {
#         "color": "white",
#         "background-color": "#3182bd",
#         "margin": "0",
#         "padding": "5px",
#         "border-bottom": "solid thin black",
#         "border-radius": "4px"
#     },
#
#     "title-success": {
#         "color": "white",
#         "background-color": "#31a354",
#         "margin": "0",
#         "padding": "5px",
#         "border-bottom": "solid thin black",
#         "border-radius": "4px"
#     },
#
#     "title-failure": {
#         "color": "white",
#         "background-color": "#de2d26",
#         "margin": "0",
#         "padding": "5px",
#         "border-bottom": "solid thin black",
#         "border-radius": "4px"
#     },
#
#     "plotting-area": {
#         "border": "solid thin lightgrey",
#         "background-color": "#F5F6F9",
#         "padding": "10",
#         "margin-bottom": "80"
#     },
#
#     "heading": {
#         "text-align": "center",
#         "text-decoration": "underline"
#     },
#
#     "container": {
#         "border-radius": "5px",
#         "background-color": " #f9f9f9",
#         "margin": "10px",
#         "padding": "15px",
#         "position": "relative",
#         "box-shadow": "2px 2px 2px lightgrey"
#
#     }
# }


# Read data
Confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
Deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
Recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")


report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")
report.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', "Confirmed", "Deaths"]

report.loc[:, "Confirmed"] = report.loc[:, "Confirmed"].fillna(0)

report["text"] = (report["Country/Region"] + "<br>" + report["Province/State"] + "<br>Confirmed cases: " +
                  report["Confirmed"].astype(str) + "<br>Deaths: " + report["Deaths"].astype(str))

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

import plotly.express as px

bubble = np.log2(report.Confirmed + 1)
fig = px.scatter_mapbox(report, lat="Lat", lon="Long", hover_name="Province/State", hover_data=["Country/Region", "Confirmed"],
                        color_discrete_sequence=["red"], zoom=1.5, height=800, size=bubble)
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


fig2 = px.scatter_geo(report, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble, height=800, projection="orthographic",
                      color_discrete_sequence=["red"], text="text")

fig2.update_layout(
    title_text='TOTAL CONFIRMED:' + str(sum(report["Confirmed"])) + '<br>' +
               'TOTAL DEATHS:' + str(sum(report["Deaths"])),
)

bubble2 = np.log2(globalreport.Confirmed + 1)
fig3 = px.scatter_geo(globalreport, lat="Lat", lon="Long",
                     hover_name="Country/Region", size=bubble2, height=800,
                     animation_frame="Date",
                     projection="natural earth")

fig3.update_layout(
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
fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# app.layout = html.Div([
#     dcc.Tabs([
#         dcc.Tab(label='Tab one', children=[
#             dcc.Graph(
#                 figure=fig
#             )
#         ]),
#         dcc.Tab(label='Tab two', children=[
#             dcc.Graph(
#                 figure=fig2
#             )
#         ]),
#         dcc.Tab(label='Tab three', children=[
#             dcc.Graph(
#                 figure=fig3
#             )
#         ]),
#     ])
# ])


app.layout = html.Div([
    html.H1('COVID-19'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Tab One', value='tab-1'),
        dcc.Tab(label='Tab Two', value='tab-2'),
        dcc.Tab(label='Tab Three', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dac.TabItem(id='content_value_boxes',

                        children=[
                            html.Div([
                                dac.InfoBox(
                                    title="TOTAL CONFIRMED ",
                                    value=sum(report["Confirmed"]),
                                    gradient_color="danger",
                                    icon="envelope"
                                ),
                                dac.InfoBox(
                                    title="TOTAL RECOVERED",
                                    gradient_color="success",
                                    value=sum(Recovered.iloc[:, -1]),
                                    icon="comments"
                                ),
                                dac.InfoBox(
                                    title="TOTAL DEATHS",
                                    color="black",
                                    value=sum(report["Deaths"]),
                                    icon="bookmark"
                                )
                            ], className='row')
                        ]
                        ),
            dcc.Graph(
                id='graph-1-tabs',
                figure=fig
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs',
                figure=fig2
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3'),
            dcc.Graph(
                id='graph-3-tabs',
                figure=fig3
            )
        ])


value_boxes_tab = dac.TabItem(id='content_value_boxes',

                              children=[
                                  html.H4('Value Boxes'),
                                  html.Div([
                                      dac.ValueBox(
                                          value=150,
                                          subtitle="New orders",
                                          color="primary",
                                      ),
                                      dac.ValueBox(
                                          elevation=4,
                                          value="53%",
                                          subtitle="New orders",
                                          color="danger",
                                      ),
                                      dac.ValueBox(
                                          value="44",
                                          subtitle="User Registrations",
                                          color="warning",
                                          icon="suitcase"
                                      ),
                                      dac.ValueBox(
                                          value="53%",
                                          subtitle="Bounce rate",
                                          color="success",
                                          icon="database"
                                      )
                                  ], className='row')
                              ]
                              )

app.run_server(port=5054, debug=True)