import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np

application = dash.Dash()
x = np.array([1, 2, 3, 4, 5])

title = html.H1('Stock Tracker')

application.layout = html.Div([
    title,
    html.P('testing... testing...'),
    dcc.Graph(figure={
        'data': [
            {'x': x, 'y': x, 'type': 'line', 'name': 'linear'},
            {'x': x, 'y': x**2, 'type': 'line', 'name': 'exponential'},
        ],
        'layout': {'title': 'Test graph'}
    })
])

if __name__ == '__main__':
    application.run_server(debug=True)
