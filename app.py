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

# Read data
Confirmed = pd.read_csv(
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
Deaths = pd.read_csv(
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
Recovered = pd.read_csv(
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")
report.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', "Confirmed", "Deaths"]

report.loc[:, "Confirmed"] = report.loc[:, "Confirmed"].fillna(0)

report["text"] = (report["Country/Region"].str.upper() + "<br>" + report["Province/State"] + "<br>Confirmed cases: " +
                  report["Confirmed"].astype(str) + "<br>Deaths: " + report["Deaths"].astype(str))

date = pd.to_datetime(Confirmed.columns[4:-1])

conf2 = pd.melt(Confirmed, id_vars=Confirmed.columns[0:4])

deaths2 = pd.melt(Deaths, id_vars=Deaths.columns[0:4])

globalreport = pd.concat([conf2, deaths2.value], axis=1)
globalreport.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', 'Date', 'Confirmed', 'Deaths']

globalreport['Country/Region'] = pd.Categorical(globalreport['Country/Region'])

factors = sorted(globalreport['Country/Region'].unique())

import plotly.express as px

bubble = np.log2(report.Confirmed + 1)
fig = px.scatter_mapbox(report, lat="Lat", lon="Long", hover_name="Country/Region",
                        hover_data=["Province/State", "Confirmed", "Deaths"],
                        color_discrete_sequence=["red"], zoom=1.5, height=800, size=bubble)
fig.data[0].update(hovertemplate= '<b>%{hovertext}</b><br>%{customdata[0]}<br>Confirmed:%{customdata[1]}<br>Deaths:%{'
                                  'customdata[2]}')
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
fig.update_layout(
    template="plotly_dark",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

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
fig3.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

fig4 = go.Figure(data=go.Scattergeo(
    lon=report['Long'],
    lat=report['Lat'],
    hovertext=report["text"],
    hoverinfo="text",
    mode='markers',
    marker=dict(
        size=bubble,
        opacity=0.8,
        color="red"
    )
)
)
fig4.update_geos(
    showcountries=True,
    showland=True,
    projection_type="orthographic",
    landcolor="green",
    oceancolor="MidnightBlue",
    showocean=True,
    lakecolor="LightBlue"
)

fig4.update_layout(
    height=700,
    template="plotly_dark",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN]
)

TAB_STYLE = {
    'border': 'none',
    'boxShadow': 'inset 0px -1px 0px 0px lightgrey',
    'background': '#033C73',
    'paddingTop': 0,
    'paddingBottom': 0,
    'height': '42px',
    'font-size': '100%',
    'color': 'white'
}

SELECTED_STYLE = {
    'boxShadow': 'none',
    'borderLeft': 'none',
    'background': '#022b52',
    'borderRight': 'none',
    'borderTop': 'none',
    'borderBottom': '2px #004A96 solid',
    'paddingTop': 0,
    'paddingBottom': 0,
    'height': '42px',
    'font-size': '150%'
}


app.layout = html.Div([
    html.H1('COVID-19'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Latest data', value='tab-1', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
        dcc.Tab(label='Evolution', value='tab-2', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
        dcc.Tab(label='Tab Three', value='tab-3', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
        dcc.Tab(label='Tab Four', value='tab-4', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
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
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4'),
            dcc.Graph(
                id='graph-4-tabs',
                figure=fig4
            )
        ])


app.run_server(port=5054, debug=True)