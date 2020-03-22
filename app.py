import dash
import dash_bootstrap_components as dbc  # import the library
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np
import json

# Read data
Confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                        "/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
Deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                     "/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
Recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                        "/csse_covid_19_time_series/time_series_19-covid-Recovered.csv")

report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1], Recovered.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")
report.columns.values[[4, 5, 6]] = ["Confirmed", "Deaths", "Recovered"]


