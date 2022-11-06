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
df_date = df.groupby("Online")["wf_count"].count()  # MOVE TO FILTERED DATA
df_date = df_date.to_frame()
df_date = df_date.reset_index()
date_min = df_date["Online"].min()
date_max = df_date["Online"].max()

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

load_figure_template("MINTY")
app.title = "UK Onshore Wind Farm Data"


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
                dcc.RangeSlider(
                    date_min, date_max, 1, value=[date_min, date_max], id="date-slider"
                ),
            ],
            id="date_slider",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": Developer, "value": Developer}
                        for Developer in np.sort(df.Developer.unique())
                    ],
                    value=df.Developer[127],
                    multi=True,
                    id="developer",
                    clearable=True,
                )
            ],
            id="drop-container-1",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": Operator, "value": Operator}
                        for Operator in np.sort(df.Operator.unique())
                    ],
                    value=df.Operator[127],
                    multi=True,
                    id="operator",
                    clearable=True,
                )
            ],
            id="drop-container-2",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": Owner, "value": Owner}
                        for Owner in np.sort(df.Owner.unique())
                    ],
                    value=df.Owner[127],
                    multi=True,
                    id="owner",
                    clearable=True,
                )
            ],
            id="drop-container-3",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=[
                        {"label": turbine_manufacturer, "value": turbine_manufacturer}
                        for turbine_manufacturer in np.sort(
                            df.turbine_manufacturer.unique()
                        )
                    ],
                    value=df.turbine_manufacturer[127],
                    multi=True,
                    id="manufacturer",
                    clearable=True,
                )
            ],
            id="drop-container-4",
        ),
        html.Div(
            [dcc.Graph(id="wf-count", className="card")],
            id="card-1",
        ),
        html.Div(
            [dcc.Graph(id="mw-count", className="card")],
            id="card-2",
        ),
        html.Div(
            [dcc.Graph(id="tur-count", className="card")],
            id="card-3",
        ),
        html.Div(
            [dcc.Graph(id="map")],
            id="map-cont",
        ),
        html.Div(
            [dcc.Graph(id="bar-main")],
            id="wfarms",
            style={"overflowY": "scroll", "height": "1000"},
        ),
        html.Div([dcc.Graph(id="pie-country", className="donut")], id="donut-1"),
        html.Div([dcc.Graph(id="pie-operator", className="donut")], id="donut-2"),
        html.Div([dcc.Graph(id="pie-manuf", className="donut")], id="donut-3"),
        html.Div([dcc.Graph(id="line-date", className="online")], id="online"),
    ],
    id="container",
)


@app.callback(
    [
        Output("wf-count", "figure"),
        Output("mw-count", "figure"),
        Output("tur-count", "figure"),
        Output("map", "figure"),
        Output("bar-main", "figure"),
        Output("pie-country", "figure"),
        Output("pie-operator", "figure"),
        Output("pie-manuf", "figure"),
        Output("line-date", "figure"),
    ],
    [
        Input("developer", "value"),
        Input("operator", "value"),
        Input("owner", "value"),
        Input("manufacturer", "value"),
        Input("date-slider", "value"),
    ],
)
def update_charts(
    selected_dev,
    selected_op,
    selected_owner,
    selected_manuf,
    selected_dates,
):
    mask_main = (
        (df.Developer == selected_dev)
        & (df.Operator == selected_op)
        & (df.Owner == selected_owner)
        & (df.turbine_manufacturer == selected_manuf)
    )
    filtered_data = df.loc[mask_main, :]
    count = len(filtered_data)
    WtgTotal = filtered_data["No."].sum()
    instCap = filtered_data["Cap. (MW)"].sum() / 1000

    mask_date = (df_date.Online >= selected_dates[0]) & (
        df_date.Online <= selected_dates[1]
    )
    filtered_data_date = df_date.loc[mask_date, :]

    figWfCount = go.Figure(
        go.Indicator(
            mode="number",
            value=count,
            title={"text": "Wind Farm Developments", "font": {"size": 20}},
            number={"font": {"size": 50}},
        ),
    )

    figWfCount.update_layout(
        paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5)
    )

    figMwCount = go.Figure(
        go.Indicator(
            mode="number",
            value=instCap,
            title={"text": "Installed Capacity", "font": {"size": 20}},
            number={"font": {"size": 50}},
        )
    )

    figMwCount.update_layout(
        paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5)
    )

    figTurCount = go.Figure(
        go.Indicator(
            mode="number",
            value=WtgTotal,
            title={"text": "Installed Turbines", "font": {"size": 20}},
            number={"font": {"size": 50}},
        )
    )

    figTurCount.update_layout(
        paper_bgcolor="lightgray", margin=dict(l=50, r=50, t=30, b=5)
    )

    figMap = px.scatter_mapbox(
        filtered_data,
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

    figBarWf = px.bar(
        filtered_data,
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
        filtered_data,
        values="Cap. (MW)",
        names="country",
        title="Cap. (MW) by country",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    figPieMwC.update_traces(textinfo="value", textposition="inside")
    figPieMwC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figPieWfC = px.pie(
        filtered_data,
        values="wf_count",
        names="Operator",
        title="Wind Farm count by Operator",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    figPieWfC.update_traces(textinfo="value", textposition="inside")
    figPieWfC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figPieManuf = px.pie(
        filtered_data,
        values="No.",
        names="turbine_manufacturer",
        title="Installed Turbines",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    figPieManuf.update_traces(textinfo="value", textposition="inside")
    figPieManuf.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figOnline = px.line(
        filtered_data_date, x="Online", y="wf_count", title="Wind Farms online by year"
    )

    return (
        figWfCount,
        figMwCount,
        figTurCount,
        figMap,
        figBarWf,
        figPieMwC,
        figPieWfC,
        figPieManuf,
        figOnline,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
