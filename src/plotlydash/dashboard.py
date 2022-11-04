import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
from src.SHIKI_API import ShiNoAuth
import plotly.express as px
# from .layout import html_layout
from src.member_list import members
import random

def init_dashboard(server, **kwargs):
    """Create a Plotly Dash dashboard."""
    html_layout = kwargs.pop('html_layout',)

    a = ShiNoAuth()

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dashapp/",
        external_stylesheets=[
            "/static/dist/css/styles.css",
            "https://fonts.googleapis.com/css?family=Lato",
        ],
    )
    # add web page layout to dash layout
    dash_app.index_string = html_layout
    init_member = random.choice(members)
    df = a.get_df_w_ptw(init_member) # random member
    fig = px.histogram(df, 
            y="type", x='size',
            # color=df.loc[:, 'size'].to_dict(),
            color='size',
            color_discrete_sequence=['#e5d82a','#abda52','#2de133','#0cb5e4', '#ab2626'],
            width=800, 
            height=400, 
            title=f'Stats for user: {init_member}'
        )
    fig = fig.update_traces(showlegend=True, )

    dash_app.layout = html.Div([
        html.Div([
        # title
        html.H3('Stats from shikimori.one:',
                style={'float': 'left',
                       }),
        ]),
        # wathed/planned histogram
        dcc.Dropdown(
            id='dropdown',
            options=[{'label': member, 'value': member} for member in members],
            value=[init_member],
            multi=True
        ),
        dcc.Graph(id='graph', figure=fig),
        # scores
        # dcc.Dropdown(
        #     id='dropdown_scores',
        #     options=[{'label': member, 'value': member} for member in members],
        #     value=[init_member],
        #     multi=True
        # ),
        dcc.Graph(id='graph_scores', figure=fig),
        # types
        # dcc.Dropdown(
        #     id='dropdown_types',
        #     options=[{'label': member, 'value': member} for member in members],
        #     value=[init_member],
        #     multi=True
        # ),
        dcc.Graph(id='graph_types', figure=fig),
        # ratings
        # dcc.Dropdown(
        #     id='dropdown_ratings',
        #     options=[{'label': member, 'value': member} for member in members],
        #     value=[init_member],
        #     multi=True
        # ),
        dcc.Graph(id='graph_ratings', figure=fig),

    ])

    # засунуть в класс обработчика апи
    def get_fig(dropdown, title):
        df = a.get_df_w_ptw(str(dropdown[-1])) #member
        fig = px.histogram(
            df,
            y="type",
            x='size',
            color='size',
            color_discrete_sequence=[
                '#e5d82a',
                '#abda52',
                '#2de133',
                '#0cb5e4',
                '#ab2626',
            ],
            width=800,
            height=400,
            title=f'{title} for user: {dropdown[-1]}',
        )

        fig.update_traces(showlegend=True, )
        return fig

    @dash_app.callback(Output('graph', 'figure'), [Input('dropdown', 'value')])
    def update_graph(dropdown):
        return get_fig(dropdown, 'Stats')

    @dash_app.callback(Output('graph_scores', 'figure'), [Input('dropdown', 'value')])
    def update_graph(dropdown):
        return a.get_fig(a.get_df_scores(dropdown[-1]), 'Scores', dropdown[-1], 'stars', 'amount', )

    @dash_app.callback(Output('graph_ratings', 'figure'), [Input('dropdown', 'value')])
    def update_graph(dropdown):
        return a.get_fig(a.get_df_ratings(dropdown[-1]), 'Ratings', dropdown[-1], 'rate', 'amount', )

# непправильные имена иногда проскакивают
    @dash_app.callback(Output('graph_types', 'figure'), [Input('dropdown', 'value')])
    def update_graph(dropdown):
        return a.get_fig(a.get_df_types(dropdown[-1]), 'Types', dropdown[-1], 'name', 'amount', )

    return dash_app.server


if __name__ == '__main__':
    # at http://127.0.0.1:8008/dashapp/
    init_dashboard(True).run(debug=True, port=8008)