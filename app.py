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
# df_date = df.groupby("Online")["wf_count"].count()  # MOVE TO FILTERED DATA
# df_date = df_date.to_frame()
# df_date = df_date.reset_index()
# date_min = df_date["Online"].min()
# date_max = df_date["Online"].max()

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
                html.Img(src="assets/wind-farm.png", className="img-tur"),
            ],
            id="navbar-1",
        ),
        html.Div(
            [
                html.H3("UK Onshore Wind Farms", className="head"),
            ],
            id="navbar-2",
        ),
        html.Div(
            [
                dbc.Button(
                    "Reset",
                    href="javascript:window.location.reload();",
                    className="reset",
                    color="danger",
                ),
            ],
            id="navbar-3",
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
        html.Hr(style={"borderWidth": "0.3vh", "width": "25%", "color": "#FEC700"}),
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
                                "Online",
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
        # html.Div(
        # [
        # dcc.RangeSlider(
        # date_min, date_max, 1, value=[date_min, date_max], id="date-slider"
        # ),
        # ],
        # id="date_slider",
        # ),
        html.Div(
            [dcc.Graph(id="map", className="map-vis")],
            id="map-cont",
        ),
        html.Div(
            [dcc.Graph(id="bar-main", className="wf-bar")],
            id="wfarms",
            style={"overflow": "scroll", "height": 800},
        ),
        html.Hr(className="hr", id="hr-1"),
        html.Div([dcc.Graph(id="pie-country", className="donut")], id="donut-1"),
        html.Div([dcc.Graph(id="pie-operator", className="donut")], id="donut-2"),
        html.Div([dcc.Graph(id="pie-manuf", className="donut")], id="donut-3"),
        html.Hr(className="hr", id="hr-2"),
        html.Div([dcc.Graph(id="line-date", className="online")], id="online"),
        html.Hr(className="hr", id="hr-3"),
        html.Center(
            children=[
                html.Span(children="© "),
                html.Span(children="John Davidson"),
                html.Span(children=" | "),
                html.A(
                    children="john.davidson.ctr@hotmail.co.uk",
                    href="mailto:john.davidson.ctr@hotmai.co.uk",
                ),
                html.Br(),
                html.Span(children="built with "),
                html.A(
                    children="Plotly Dash",
                    href="https://plotly.com/dash/open-source/",
                ),
                html.Span(children=" & "),
                html.A(
                    children="Dash Bootstrap Components",
                    href="https://dash-bootstrap-components.opensource.faculty.ai/",
                ),
                html.Br(),
                html.Span(children="Turbines icon from "),
                html.A(
                    children="Flaticon",
                    href="https://www.flaticon.com/free-icons/wind-farm",
                ),
            ],
            id="footer",
        ),
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
        # Input("date-slider", "value"),
    ],
)

# def update_charts(selected_category, selection, selected_dates):


def update_charts(selected_category, selection):

    filtered_data = df[df[selection] == selected_category]

    count = len(filtered_data)
    WtgTotal = filtered_data["No."].sum()
    instCap = filtered_data["Cap. (MW)"].sum() / 1000

    # df_fil_date = filtered_data.groupby("Online")["wf_count"].count()
    # df_fil_date = df_fil_date.to_frame()
    # df_fil_date = df_fil_date.reset_index()

    # mask_date = (df_fil_date.Online >= selected_dates[0]) & (
    # df_fil_date.Online <= selected_dates[1]
    # )
    # filtered_data_date = df_fil_date.loc[mask_date, :]

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
        color="Cap. (MW)",
        # size="Cap. (MW)",
        color_continuous_scale=px.colors.sequential.Rainbow
        # color_discrete_sequence=["green"],
    )

    figMap.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(center=dict(lat=54.951985, lon=-2.494792), pitch=0, zoom=5),
        showlegend=False,
    )

    figMap.update_traces(marker={"size": 10})

    figBarWf = px.bar(
        filtered_data,
        x="Cap. (MW)",
        y="Wind farm",
        color="country",
        title="Cap (MW) by Wind Farm",
        hover_name="Wind farm",
        hover_data={
            "Wind farm": False,
            "Power per turbine (MW)": True,
            "No.": True,
            "Cap. (MW)": True,
            "Online": True,
            "Developer": True,
            "Operator": True,
            "Owner": True,
            "country": True,
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
        # color_discrete_sequence=px.colors.qualitative.G10,
    )

    barWfHeight = len(filtered_data) * 30
    if barWfHeight == 0:
        barWfHeight = 800
    if barWfHeight <= 300:
        barWfHeight = len(filtered_data) * 100
    if barWfHeight <= 100:
        barWfHeight = len(filtered_data) * 175

    figBarWf.update_layout(
        autosize=False,
        height=barWfHeight,
        bargap=0,
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
    )
    figBarWf.update_traces(marker_color="green")

    figPieMwC = px.pie(
        filtered_data,
        values="Cap. (MW)",
        names="country",
        title="Cap. (MW) by country",
        hole=0.5,
        color="country",
        # color_discrete_sequence=px.colors.qualitative.G10,
        color_discrete_map={
            "scotland": "#3366CC",
            "england": "#DC3912",
            "wales": "#109618",
            "northern ireland": "#FF9900",
        },
        # category_orders={
        # "country": ["scotland", "england", "wales", "northern ireland"]
        # },
    )
    figPieMwC.update_traces(textinfo="value", textposition="inside")
    figPieMwC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figPieWfC = px.pie(
        filtered_data,
        values="wf_count",
        names="Operator",
        title="Wind Farm count by Operator",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    figPieWfC.update_traces(textinfo="value", textposition="inside")
    figPieWfC.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figPieManuf = px.pie(
        filtered_data,
        values="No.",
        names="turbine_manufacturer",
        title="Installed Turbines",
        color="turbine_manufacturer",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    figPieManuf.update_traces(textinfo="value", textposition="inside")
    figPieManuf.update_layout(margin=dict(l=0, r=0, t=50, b=0))

    figOnline = px.bar(
        filtered_data,
        x="Online",
        y="wf_count",
        color="country",
        title="Wind Farms online by year",
        hover_name="Wind farm",
        # color_discrete_sequence=px.colors.qualitative.G10,
        color_discrete_map={
            "scotland": "#3366CC",
            "england": "#DC3912",
            "wales": "#109618",
            "northern ireland": "#FF9900",
        },
    )
    figOnline.update_layout(
        showlegend=True,
        yaxis=dict(tickmode="linear", tick0=1, dtick=1),
    )
    # figOnline.update_traces(marker_color="green")
    figOnline.update_xaxes(type="category", categoryorder="category ascending")

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
