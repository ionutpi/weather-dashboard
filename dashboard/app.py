import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
colors = {"background": "white", "text": "darkblue"}

def degree_to_direction(degrees):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(degrees / (360. / len(dirs)))
    return dirs[ix % len(dirs)]

def serve_layout():
    engine = create_engine('mysql+mysqlconnector://testuser:testpassword@db/dash')
    df = pd.read_sql_table('weather', engine).drop_duplicates()
    wind_long = df[df["parameterId"].isin(["wind_dir", "wind_speed"])]
    wind_pivot = pd.pivot(wind_long, columns=['parameterId'], values=['value'], index=['observed'])
    wind_pivot.columns = wind_pivot.columns.droplevel()
    wind_pivot["direction"] = wind_pivot["wind_dir"].map(degree_to_direction)
    wind_pivot["strength"] = pd.cut(
        wind_pivot["wind_speed"], 
        bins=[0, 2, 4, 6, 8, 10, 1000], 
        labels=['0-2', '2-4', '4-6', '6-8', '8-10', '10+']
    )
    wind_df = wind_pivot.groupby(["direction", "strength"]).count().reset_index()
    wind_df["frequency"] = wind_df["wind_speed"]
    wind_rose = px.bar_polar(
        wind_df,
        r="frequency",
        theta="direction",
        color="strength",
        color_discrete_sequence=px.colors.sequential.Plasma_r,
    )
    wind_rose.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        showlegend=False,
    )
    temp_df = (
        df[df["parameterId"] == "temp_dry"]
        .groupby("observed")
        .mean()["value"]
        .reset_index()
    )
    temp_bar = px.line(temp_df, x="observed", y="value")
    temp_bar.update_layout(yaxis_title=None, xaxis_title=None)
    humidity_df = (
        df[df["parameterId"] == "humidity"]
        .groupby("observed")
        .mean()["value"]
        .reset_index()
    )
    humidity_bar = px.line(humidity_df, x="observed", y="value")
    humidity_bar["data"][0]["line"]["color"] = "rgb(204, 204, 204)"
    humidity_bar["data"][0]["line"]["width"] = 5
    humidity_bar.update_layout(yaxis_title=None, xaxis_title=None)

    page = html.Div(
        style={"backgroundColor": colors["background"]},
        children=[
            html.H1(
                children="Weather dashboard",
                style={
                    "textAlign": "center",
                    "color": colors["text"],
                    "margin-bottom": "35px",
                },
            ),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div("Temperature", style={"text-align": "center"})
                            ),
                            dbc.Col(html.Div("Wind", style={"text-align": "center"})),
                            dbc.Col(html.Div("Humidity", style={"text-align": "center"})),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(dcc.Graph(id="temp_bar", figure=temp_bar)),
                            dbc.Col(dcc.Graph(id="wind_rose", figure=wind_rose)),
                            dbc.Col(dcc.Graph(id="humidity_bar", figure=humidity_bar)),
                        ]
                    ),
                ]
            ),
        ],
    )
    return page

app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port='7080', debug=False)
