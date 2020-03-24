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
Confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                        "/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
Deaths = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                     "/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
Recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data"
                        "/csse_covid_19_time_series/time_series_19-covid-Recovered.csv")

report = pd.concat([Confirmed.iloc[:, [0, 1, 2, 3, -1]], Deaths.iloc[:, -1], Recovered.iloc[:, -1]], axis=1)
report.loc[:, "Province/State"] = report.loc[:, "Province/State"].fillna("")
report.columns.values[[4, 5, 6]] = ["Confirmed", "Deaths", "Recovered"]

date = pd.to_datetime(Confirmed.columns[4:-1])

conf2 = pd.melt(Confirmed, id_vars=Confirmed.columns[0:4])
dates = pd.to_datetime(conf2.variable)
conf2.variable = dates

deaths2 = pd.melt(Deaths, id_vars=Deaths.columns[0:4])
recovered2 = pd.melt(Recovered, id_vars=Recovered.columns[0:4])

globalreport = pd.concat([conf2, deaths2.value, recovered2.value], axis=1)
globalreport.columns.values[[4, 5, 6, 7]] = ["Date", "Confirmed", "Deaths", "Recovered"]

globalreport['Country/Region'] = pd.Categorical(globalreport['Country/Region'])
# print(globalreport.dtypes)

factors = sorted(globalreport['Country/Region'].unique())



