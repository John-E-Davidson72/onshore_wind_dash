import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# import json

df = pd.read_csv("wtg_df_all.csv")
countWf = len(df)
WtgTotal = df["No."].sum()
instCap = df["Cap. (MW)"].sum() / 1000
df_date = df.groupby("Online")["wf_count"].count()
df_date = df_date.to_frame()
df_date = df_date.reset_index()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, maximum-scale=1",
        }
    ],
)
# app = dash.Dash(__name__)
load_figure_template("MINTY")
app.title = "UK Onshore Wind Farm Data"

figMap = px.scatter_mapbox(
    df,
    lat="lat",
    lon="long",
    hover_name="Wind farm",
    hover_data=[
        "Cap. (MW)",
        "Developer",
        "Operator",
        "Owner",
        "Online",
        "turbine_manufacturer",
    ],
    color_discrete_sequence=["green"],
)

figMap.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=dict(center=dict(lat=54.951985, lon=-2.494792), pitch=0, zoom=5),
)

figWfCount = go.Figure(
    go.Indicator(
        mode="number",
        value=countWf,
        title={"text": "Wind Farm Developments", "font": {"size": 20}},
        number={"font": {"size": 50}},
    ),
)
figWfCount.update_layout(paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5))
figMwCount = go.Figure(
    go.Indicator(
        mode="number",
        value=instCap,
        title={"text": "Installed Capacity", "font": {"size": 20}},
        number={"font": {"size": 50}},
    )
)
figMwCount.update_layout(paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5))

figTurCount = go.Figure(
    go.Indicator(
        mode="number",
        value=WtgTotal,
        title={"text": "Installed Turbines", "font": {"size": 20}},
        number={"font": {"size": 50}},
    )
)
figTurCount.update_layout(paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5))

# count = len(df)
# widths = [0.8 for x in range(count)]

figBarWf = px.bar(
    df,
    x="Cap. (MW)",
    y="Wind farm",
    color="country",
    title="Cap (MW) by Wind Farm",
    hover_name="Wind farm",
    hover_data={
        "Power per turbine (MW)": True,
        "No.": True,
        "Cap. (MW)": True,
        "Online": True,
        "Developer": True,
        "Operator": True,
        "Owner": True,
        "country": False,
        "lat": False,
        "long": False,
        "wf_count": False,
        "turbine_manufacturer": True,
        "turbine_model": True,
        "state": False,
    },
    orientation="h",
    width=10,
    labels={"Wind farm": "Wind farm name", "Cap. (MW)": "Installed Capacity (MW)"},
    color_discrete_sequence=px.colors.qualitative.G10,
)

figPieMwC = px.pie(
    df,
    values="Cap. (MW)",
    names="country",
    title="Cap. (MW) by country",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.G10,
)
figPieMwC.update_traces(textinfo="value", textposition="inside")
figPieMwC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

figPieWfC = px.pie(
    df,
    values="wf_count",
    names="Operator",
    title="Wind Farm count by Operator",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.G10,
)
figPieWfC.update_traces(textinfo="value", textposition="inside")
figPieWfC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

figPieManuf = px.pie(
    df,
    values="No.",
    names="turbine_manufacturer",
    title="Installed Turbines",
    hole=0.5,
    color_discrete_sequence=px.colors.qualitative.G10,
)
figPieManuf.update_traces(textinfo="value", textposition="inside")
figPieManuf.update_layout(margin=dict(l=0, r=0, t=50, b=0))

figOnline = px.line(
    df_date, x="Online", y="wf_count", title="Wind Farms online by year"
)

# app.layout = html.Div(
# [
# html.H1("UK Onshore Wind Farms"),
# dcc.Graph(figure=figMap),
# dcc.Graph(figure=figWfCount),
# ],
# id="left-container",
# )

app.layout = html.Div(
    [
        html.Div(
            [
                html.H3("UK Onshore Wind Farms"),
                # html.Img(src="assets/tbc.png"),
            ],
            id="navbar",
        ),
        html.Div(
            [
                html.H5("Selections"),
                html.P("put callbacks here"),
                # html.Img(src="assets/tbc.png"),
            ],
            id="left-container",
        ),
        html.Div(
            [dcc.Graph(figure=figWfCount, className="card")],
            id="card-1",
        ),
        html.Div(
            [dcc.Graph(figure=figMwCount, className="card")],
            id="card-2",
        ),
        html.Div(
            [dcc.Graph(figure=figTurCount, className="card")],
            id="card-3",
        ),
        html.Div(
            [dcc.Graph(figure=figMap)],
            id="map",
        ),
        html.Div(
            [dcc.Graph(figure=figBarWf)],
            id="wfarms",
            style={"overflowY": "scroll", "height": "1000"},
        ),
        html.Div([dcc.Graph(figure=figPieMwC, className="donut")], id="donut-1"),
        html.Div([dcc.Graph(figure=figPieWfC, className="donut")], id="donut-2"),
        html.Div([dcc.Graph(figure=figPieManuf, className="donut")], id="donut-3"),
        html.Div([dcc.Graph(figure=figOnline, className="online")], id="online"),
    ],
    id="container",
)


if __name__ == "__main__":
    app.run_server(debug=True)
