import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
main_output = html.Div(id='main_out', children='')

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
    dash.dependencies.Output('main_out', 'children'),
    [dash.dependencies.Input('sub_button', 'n_clicks')],
    [dash.dependencies.State('search', 'value')]
)
def search(n_clicks, value):
    return f'You searched for {value}'


if __name__ == '__main__':
    app.run_server(debug=True)
