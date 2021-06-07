import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import datetime
import locale
import os
import pyodbc
import pandas as pd
import numpy as np
# from fbprophet import Prophet
import os

#locale.setlocale(locale.LC_TIME, 'es_pe')

external_scripts = [
        "https://code.jquery.com/jquery-3.3.1.slim.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js"
        ]

external_stylesheets = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css"
        ]


app = dash.Dash(
    __name__,
    requests_pathname_prefix= "/" if (__name__ == '__main__') else '/wsgi/',
    external_scripts = external_scripts,
    external_stylesheets = external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

candidate01 = dict(
    id='00000007',
    name="Keiko Fujimori",
    picture=app.get_asset_url(r'images/00000007.jpg')
)
candidate02 = dict(
    id='00000014',
    name="Pedro Castillo",
    picture=app.get_asset_url(r'images/00000014.jpg')
)


def ftext(candidate, x,y,z, per):
    txtnormal = ''
    if per != None:
        txtnormal = '<b>Avance al: </b>{per}<br>'.format(per=str('{:.2%}'.format(per)))
    txtnormal = txtnormal + '''<b>{candidate}: </b>{x}
            <br><b>Total Votos: </b>{y}'''.format(candidate=candidate, x=str(x*100)+"%",y=f'{y:,}')
    if(z >= 0):
        txtnormal = txtnormal + '<br><b>Diferencia de Votos: </b>{z}'.format(z=f'{z:,}')
    return txtnormal

def navbar():
    return html.Nav([
        html.Div([
            html.Div([
                html.Span('PRESENTACIÓN DE RESULTADOS', className='text-center')
            ], className='text-center ms-auto me-auto')
        ], className='container-fluid text-center')
    ], className='navbar navbar-expand-lg navbar-light bg-light fixed-top')


def cardCandidate(candidate):
    return html.Div([
        html.Div(candidate["name"], className="col-12"),
        html.Div([html.Img(src=candidate["picture"], className='card-img-bottom text-center', style={"height": '90px', 'max-width':'90px'})], className="col-12")

    ], className="row g-0 text-center")

def progressBar(cp, kc, cc):
    return html.Div([
        html.Div("Elecciones Perú", className="col-12 text-center"),
        html.Div("Al "+'{:.2%}'.format(cp), className="col-12 text-center"),
        html.Span("▼", className="col-12 text-center"),
        html.Div(
            html.Div([
                # html.Span("|", className="", style={'position': 'absolute', 'right':0, 'left':0, 'top': 15, 'font-size':'40px', 'font-weight': 'lighter'}),
                html.Div('{:.2%}'.format(cc),className="progress-bar", style={'width': '{:.2%}'.format(cc)}),
                html.Div('{:.2%}'.format(kc),className="progress-bar bg-warning", style={'width': '{:.2%}'.format(kc)})
            ], className='progress text-center', style={'height': '40px'}
        ), className="col-12"),
    ], className="row g-0")

def serve_layout():
    df = pd.read_csv('data\\onpe.csv', sep='|')

    df_Fujimori = df[df['Partido'] == 'FUERZA POPULAR']
    df_Castillo = df[df['Partido'] == 'PARTIDO POLITICO NACIONAL PERU LIBRE']
    df_avance = df['Avance'].unique()

    x_data = [x/100 for x in df_avance]

    keiko_data = df_Fujimori['PerValidos'].to_numpy()
    keiko_data = [x/100 for x in keiko_data]

    castillo_data = df_Castillo['PerValidos'].to_numpy()
    castillo_data = [x/100 for x in castillo_data]

    keiko_tvotes = df_Fujimori['TotalVotos'].to_numpy()
    keiko_tvotes = [int(x.replace(',','')) for x in keiko_tvotes]

    castillo_tvotes = df_Castillo['TotalVotos'].to_numpy()
    castillo_tvotes = [int(x.replace(',','')) for x in castillo_tvotes]

    init_percent = np.amin(x_data)
    current_percent = x_data[-1]
    keiko_current = keiko_data[-1]
    castillo_current = castillo_data[-1]

    fig = go.Figure(layout=go.Layout(
            xaxis=go.layout.XAxis(title="Avance"),
            yaxis=go.layout.YAxis(title="% Votos Válidos")
        ))

    diferences = list(map(lambda x,y: x - y , keiko_tvotes,castillo_tvotes))

    hovertextKeiko = list(map(lambda x,y,z,per: ftext('Keiko Fujimori',x,y,z, per), keiko_data,keiko_tvotes, diferences, x_data))
    hovertextCastillo = list(map(lambda x,y,z: ftext('Pedro Castillo',x,y,z*-1, None), castillo_data,castillo_tvotes, diferences))

    fig.add_trace(go.Scatter(x=x_data
                            , y=keiko_data
                            , line = dict(color='rgba(236,109,0,1)', width=2)
                            , name='Keiko Fujimori'
                            , hoverinfo = "text"
                            , text = hovertextKeiko
                            , mode="lines+markers"
                 ))
    fig.add_trace(go.Scatter(x=x_data, y=castillo_data
                            , line = dict(color='rgba(7,77,217,1)', width=2)
                            , name='Pedro Castillo'
                            , hoverinfo = "text"
                            , text = hovertextCastillo
                            , mode="lines+markers"
                 ))


    #Graph styles
    fig.update(layout_showlegend=False)
    fig.update_layout(
        autosize=True,
        height=550,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=20,
            pad=0
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        ),
        xaxis = dict(
            tickformat = '.2%'
        )

    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(238,238,238,1)', range=[init_percent,1])
    fig.update_yaxes(visible=False, showgrid=False, gridwidth=1, gridcolor='rgba(238,238,238,1)')
    fig.for_each_trace(lambda t: fig.add_annotation(
        x=t.x[-1], y=t.y[-1], text=" "+'{:.2%}'.format(t.y[-1]),
        font_color=t.line.color,
        ax=10, ay=0, xanchor="left", showarrow=True
    ))
    resume_card = html.Div([
        html.Div(cardCandidate(candidate02), className="col-2 d-none d-sm-none d-md-block d-lg-block d-xl-block d-xxl-block"),
        html.Div(progressBar(current_percent, keiko_current, castillo_current), className="col-12 col-sm-12 col-md-8"),
        html.Div(cardCandidate(candidate01), className="col-2 d-none d-sm-none d-md-block d-lg-block d-xl-block d-xxl-block"),
        html.Div(cardCandidate(candidate02), className="col-6 d-block d-sm-block d-md-none d-lg-none d-xl-none d-xxl-none"),
        html.Div(cardCandidate(candidate01), className="col-6 d-block d-sm-block d-md-none d-lg-none d-xl-none d-xxl-none"),
    ], className="row g-0 mx-md-5 mx-2 mt-md-5 mt-2")

    return html.Div([
            navbar(),
            resume_card,
            html.Div(
                html.Div([
                    dcc.Graph(
                        id='presidenciales',
                        figure = fig,
                        config={
                            'displayModeBar': False,
                        }
                    ),

                    ] ,className="card-body", id="my-div"),
                className="card m-2 m-md-5",
            )
        ], className='content', id="ServeLayout")

#app layout
server = app.server

app.title = 'Presidenciales Perú'
app.layout = serve_layout


if __name__ == '__main__':
    app.run_server(debug=True)
