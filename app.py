import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

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
            [
                dcc.Dropdown(
                    id="category-dropdown",
                    options=list(
                        df[
                            [
                                "Developer",
                                "Operator",
                                "Owner",
                                "turbine_manufacturer",
                                "County",
                                "country",
                                "state",
                            ]
                        ]
                    ),
                    value="state",
                    clearable=False,
                )
            ],
            id="drop-container-1",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    multi=False,
                    id="selection-dropdown",
                    clearable=False,
                )
            ],
            id="drop-container-2",
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
            [dcc.Graph(id="map", className="map-vis")],
            id="map-cont",
        ),
        html.Div(
            [dcc.Graph(id="bar-main", className="wf-bar")],
            id="wfarms",
            style={"overflow": "scroll", "maxHeight": "800px"},
        ),
        html.Div([dcc.Graph(id="pie-country", className="donut")], id="donut-1"),
        html.Div([dcc.Graph(id="pie-operator", className="donut")], id="donut-2"),
        html.Div([dcc.Graph(id="pie-manuf", className="donut")], id="donut-3"),
        html.Div([dcc.Graph(id="line-date", className="online")], id="online"),
    ],
    id="container",
)


@app.callback(
    Output("selection-dropdown", "options"), [Input("category-dropdown", "value")]
)
def set_selection_options(selected_category):
    return [{"label": i, "value": i} for i in np.sort(df[selected_category].unique())]


@app.callback(
    Output("selection-dropdown", "value"), [Input("selection-dropdown", "options")]
)
def set_selection_value(available_options):
    return "united kingdom"


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
        Input("selection-dropdown", "value"),
        Input("category-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_charts(selected_category, selection, selected_dates):

    filtered_data = df[df[selection] == selected_category]

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
            number={"font": {"size": 50}, "suffix": "GW"},
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
        # width=10,
        labels={"Wind farm": "Wind farm name", "Cap. (MW)": "Installed Capacity (MW)"},
        color_discrete_sequence=px.colors.qualitative.G10,
    )

    figBarWf.update_layout(autosize=False, height=800)
    figBarWf.update_traces(width=1)
    figBarWf.update_xaxes(ticksuffix="  ")

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

    figOnline = px.bar(
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
