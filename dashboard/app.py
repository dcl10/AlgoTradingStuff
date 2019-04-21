import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import quandl

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

title = html.H1('Stock Tracker')
search_bar = dbc.Input(
    placeholder='Enter a holding name',
    type='text',
    value='',
    id='search'
)
search_button = dbc.Button('Go', id='sub_button', color='primary')
date_picker = dcc.DatePickerRange(id='date_range',
                                  start_date_placeholder_text='Start',
                                  end_date_placeholder_text='End')
main_output = dcc.Graph(id='stock_graph')

app.layout = dbc.Container([
    dbc.Row([title]),
    dbc.Row([
        dbc.InputGroup([
            search_bar, search_button
            ])
    ]),
    dbc.Row([html.Br()]),
    dbc.Row([date_picker]),
    dbc.Row([main_output])
])


@app.callback(
    dash.dependencies.Output('stock_graph', 'figure'),
    [dash.dependencies.Input('sub_button', 'n_clicks')],
    [dash.dependencies.State('search', 'value'),
     dash.dependencies.State('date_range', 'start_date'),
     dash.dependencies.State('date_range', 'end_date')]
)
def search_quandl(click, search, start, end):
    quandl.ApiConfig.api_key = 'b8VbyAp8ounCXxARP_Sp'
    my_data = quandl.get(search, start_date=start, end_date=end)
    return {'data': [go.Scatter(x=my_data.index, y=my_data['Adj_Close'])],
            'layout': go.Layout(xaxis={'title': 'Date'}, yaxis={'title': 'Adh. Close'})}


if __name__ == '__main__':
    app.run_server(debug=True)
