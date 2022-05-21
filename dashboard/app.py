import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
colors = {"background": "white", "text": "darkblue"}
engine = create_engine('mysql+mysqlconnector://testuser:testpassword@db/dash')

df = pd.read_sql_table('weather', engine)

wind_data = px.data.wind()

wind_rose = px.bar_polar(
    wind_data,
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

app.layout = html.Div(
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

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port='7080', debug=False)
