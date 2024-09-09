import dash
import dash_bootstrap_components as dbc  # import the library
from dash import dcc
from dash import html
import dash_admin_components as dac
from dash import dash_table
from dash.dash_table.Format import Group
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State


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
report.Confirmed = report.Confirmed.mask(report.Confirmed.lt(0), 0)


report["text"] = (report["Country/Region"].str.upper() + "<br>" + report["Province/State"] + "<br>Confirmed cases: " +
                  report["Confirmed"].astype(str) + "<br>Deaths: " + report["Deaths"].astype(str))

date = pd.to_datetime(Confirmed.columns[4:-1])

conf2 = pd.melt(Confirmed, id_vars=Confirmed.columns[0:4])

deaths2 = pd.melt(Deaths, id_vars=Deaths.columns[0:4])

recovered2 = pd.melt(Recovered, id_vars=Recovered.columns[0:4])

globalreport = pd.concat([conf2, deaths2.value, recovered2.value], axis=1)
globalreport.columns = ['Province/State', 'Country/Region', 'Lat', 'Long', 'Date', 'Confirmed', 'Deaths', 'Recovered']
globalreport.Confirmed = globalreport.Confirmed.mask(globalreport.Confirmed.lt(0), 0)

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

bubble2 = np.log2(globalreport.Confirmed + 1)
fig3 = px.scatter_geo(globalreport, lat="Lat", lon="Long",
                      hover_name="Country/Region", size=bubble2, height=800,
                      hover_data=["Province/State", "Confirmed", "Deaths"],
                      animation_frame="Date",
                      projection="natural earth")
fig3.data[0].update(hovertemplate= '<b>%{hovertext}</b><br>%{customdata[0]}<br>Confirmed:%{customdata[1]}<br>Deaths:%{'
                                  'customdata[2]}')

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN]
)

app.config['suppress_callback_exceptions'] = True

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

items_style = {
  'border': 'none',
    'boxShadow': 'inset 0px -1px 0px 0px lightgrey',
    'background': '#033C73',
    'paddingTop': 0,
    'paddingBottom': 0,
    'height': '42px',
    'font-size': '70%',
    'color': 'white',
    'width': '250px'
}


app.layout = html.Div(style={'backgroundColor': 'gray'}, children=[
    html.H1('COVID-19'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Latest data', value='tab-1', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
        dcc.Tab(label='Evolution', value='tab-2', style=TAB_STYLE,
                selected_style=SELECTED_STYLE),
        dcc.Tab(label='Data Explorer', value='tab-3', style=TAB_STYLE,
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
                                    icon="bookmark"
                                ),
                                dac.InfoBox(
                                    title="TOTAL RECOVERED",
                                    gradient_color="success",
                                    value=sum(Recovered.iloc[:, -1]),
                                    icon="bookmark"
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
            dbc.Container(
                [
                    dcc.RadioItems(
                        id='maptype',
                        options=[{'label': i, 'value': i} for i in
                                 ['National_map', 'open-street-map', 'stamen-toner', '3D']],
                        value='National_map',
                        labelStyle=items_style

                    ),
                ]
            ),
            dcc.Graph(
                id='graph-1-tabs',
                figure=fig
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Worldwide Evolution of COVID19'),
            dcc.Graph(
                id='graph-2-tabs',
                figure=fig3
            ),
            html.H2('Evolution of COVID19 by country'),
            dcc.Dropdown(
                id='country',
                options=[{'label': i, 'value': i} for i in factors],
                value=['Spain', 'Italy'],
                multi=True
            ),
            html.Div([
                html.Div([
                    dcc.Graph(id='confirmed-evolution')
                ], className="six columns", style={'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(id='death-evolution')
                ], className="six columns", style={'display': 'inline-block'}),
            ], className="row", style={'width': '100%', 'display': 'inline-block'})
        ])
    elif tab == 'tab-3':
        return html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in globalreport.columns
                ],
                data=globalreport.to_dict('records'),
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                style_table={'textAlign': 'center'},
                style_cell={'padding': '5px', 'fontSize': 12, 'textAlign': 'center'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'fontSize': 12},
            )]
        )



@app.callback(
    dash.dependencies.Output('graph-1-tabs', 'figure'),
    [dash.dependencies.Input('maptype', 'value')])
def update_graph(maptype):
    if maptype == 'National_map' or 'open-street-map' or 'stamen-toner':
        fig = px.scatter_mapbox(report, lat="Lat", lon="Long", hover_name="Country/Region",
                                hover_data=["Province/State", "Confirmed", "Deaths"],
                                color_discrete_sequence=["red"], zoom=1.5, height=800, size=bubble)
        fig.data[0].update(
            hovertemplate='<b>%{hovertext}</b><br>%{customdata[0]}<br>Confirmed:%{customdata[1]}<br>Deaths:%{'
                          'customdata[2]}')
        if maptype == 'National_map':

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
                ]
            )
        elif maptype == 'open-street-map':
            fig.update_layout(

                mapbox_style="open-street-map",
            )
        elif maptype == 'stamen-toner':
            fig.update_layout(

                mapbox_style="stamen-toner",
            )
        fig.update_layout(
            template="plotly_dark",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

    if maptype == '3D':
        fig = go.Figure(data=go.Scattergeo(
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
        fig.update_geos(
            showcountries=True,
            showland=True,
            projection_type="orthographic",
            landcolor="green",
            oceancolor="MidnightBlue",
            showocean=True,
            lakecolor="LightBlue"
        )

        fig.update_layout(
            height=700,
            template="plotly_dark",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
    return fig

@app.callback(
    [Output('confirmed-evolution', 'figure'),
     Output('death-evolution', 'figure')],
    [Input('country', 'value')])
def evolution_plot(country):
    serie = pd.Series(country, name="country")
    df = globalreport[globalreport["Country/Region"].isin(serie)]
    confirmed = px.line(df, x='Date', y='Confirmed', title='Evolution of confirmed cases', color='Country/Region')
    death = px.line(df, x='Date', y='Deaths', title='Evolution of number of deaths', color='Country/Region')
    return confirmed, death




app.run_server(port=5054, debug=True)
