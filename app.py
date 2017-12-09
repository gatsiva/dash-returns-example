import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly.graph_objs import *

import requests
import json
import pandas as pd

from datetime import date as dt

# Create an application object
app = dash.Dash()

# Define the layout
app.layout = html.Div(className='container', children=[

    html.Div(className='row', children=[
        html.Img(src="https://discourse.gatsiva.com/uploads/default/original/1X/fdfd3ffabca9cdf8c6e6fbdc9a0924e21097673b.png",
                style={
                    'height': '50px',
                    'margin-top': '20px'
                },
        ),
    ]),

    html.Div(className='row', children='''
        Prototype Visualization: Returns Analysis for Condition
    '''),

    html.Div(className='card', style={'margin-top': '20px'}, children=[
        html.Div(className='card-body', children=[
            html.P('This is a sample visualization that shows the distribution of returns after a specific price event occurs. The X axis represents the number of periods after the event occurs while the Y access represents the return percentage. Lines indicate the average and 2 standard deviation of returns.', className='card-text')
        ])
    ]),

    html.Div(className='row', style={ 'margin-top':'10px' }, children = [
        html.Div(className='col-md-6', style={ 'margin-top':'10px' }, children =[
            html.H3('Symbol'),
            html.Span('(use form \'BTC:USD:daily)\'', className='text-muted small'),
            html.Br(),
            dcc.Input(
                id='input-symbol',
                type='text',
                value='BTC:USD:daily',
                style={ 'font-size':'24px'}
            )
        ]),
        html.Div(className='col-md-6', style={ 'margin-top':'10px' }, children =[
            html.H3('API Key'),
            html.Span('Enter your personal API key', className='text-muted small'),
            html.Br(),
            dcc.Input(
                id='input-apikey',
                type='text',
                value='testkey',
                style={ 'font-size':'24px'}
            )
        ]),
        html.Div(className='col-md-6', style={ 'margin-top':'10px' }, children =[
            html.H3('Condition'),
            html.Span(
                children = [
                    'Refer to ',
                    html.A(
                        target='_new',
                        href='https://discourse.gatsiva.com/c/documentation/gatsiva-language',
                        children=['Gatsiva Language Reference']
                    ),
                    ' for syntax help.'
                ],
                className='text-muted small'),
            html.Br(),
            dcc.Textarea(
                id='input-condition',
                value='bollinger range(20,2) crosses below 0',
                style={'width': '100%','font-size': '24px'}
            )
        ]),
        html.Div(className='col-md-6', style={ 'margin-top':'10px' }, children =[
            html.H3('Date Range'),
            html.Span('Market data range to perform analysis against', className='text-muted small'),
            html.Br(),
            dcc.DatePickerRange(
                id='date-picker-range',
                display_format='YYYY-MM-DD',
                initial_visible_month=dt(2017, 10, 10),
                start_date=dt(2015, 1, 1),
                number_of_months_shown=3,
                end_date=dt.today(),
            )
        ]),
        html.Div(className='col-md-6', style={ 'margin-top':'10px' }, children =[
            html.H3('Click to Submit'),
            html.Button('Submit', id='button', className='button-sm'),
        ])
    ]),

    html.Hr(),

    html.Div('... Loading chart...', style={'align': 'center'}, id='graph-area'),


])

# Include Twitter Bootstrap stylesheet
app.css.append_css({"external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css"})

# Create the function that updates the graph via a callback. It will respond to
# button clicks from the 'button' object and take in the 'input-symbol' and
# 'input-condition' values
@app.callback(
    dash.dependencies.Output('graph-area', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [
        dash.dependencies.State('input-symbol', 'value'),
        dash.dependencies.State('input-condition', 'value'),
        dash.dependencies.State('input-apikey', 'value'),
        dash.dependencies.State('date-picker-range', 'start_date'),
        dash.dependencies.State('date-picker-range', 'end_date'),
    ]
    )
def update_output(n_clicks, symbol, condition, api_key, start_date, end_date):

    # The children to return back to the layout
    graphs = []

    if api_key == 'testkey':
        graphs.append(html.P('Please enter your actual API key above'))
    else:

        try:
            # Create the request data
            stddev_bands = 2
            request_data = {'symbol':symbol,'condition_id':1,'condition':condition,"periods":60,'from':start_date,'to':end_date}
            bearer_token = 'Bearer ' + api_key
            my_headers = {'Accept': 'application/json', 'Authorization': bearer_token}

            # Request the transaction from the API
            analytic = requests.post('https://api.gatsiva.com/api/v1/conditions/return_profile',json=request_data,headers=my_headers)

            # If we were returned a status 200
            if analytic.status_code == 200:

                # Pull out the results and format it into a pandas data frame
                results = analytic.json()['results']
                df = pd.read_json(json.dumps(results), orient='records')

                # Now add two new columns to support lines for 2x stddevs
                df['upper'] = df['mean'] + ((stddev_bands/2) * df['stddev'])
                df['lower'] = df['mean'] - ((stddev_bands/2) * df['stddev'])

                # Get the number of observations
                num_observations = results[0]['n']

                data = [
                    Scatter(
                        x=df['returnperiod'],
                        y=df['mean'],
                        name='mean'
                    ),
                    Scatter(
                        x=df['returnperiod'],
                        y=df['upper'],
                        name=str(stddev_bands) + ' stddev band upper'
                    ),
                    Scatter(
                        x=df['returnperiod'],
                        y=df['lower'],
                        name=str(stddev_bands) + ' stddev band lower'

                    )
                ]

                layout = Layout(
                    title='distribution of returns over ' + str(num_observations) + ' obs for [' + condition + '] on ' + symbol,
                    yaxis=dict(title='return'),
                    xaxis=dict(title='periods after event')
                )

                # If we got here, everything is good, so append a new graph to the graphs return object
                graphs.append(dcc.Graph(
                    id='results-plot',
                    figure={
                        'data': data,
                        'layout': layout
                        }
                ))

            # If we received an input error status code
            elif analytic.status_code == 422:

                graphs.append(html.P('Input errors detected'))
                errors = analytic.json()['errors']

                # Iterate through each error item and each item within that and just output a P tag with the items there
                for error_key, error_items in errors.items():
                    graphs.append(html.P(error_items, style={'color': 'red'}))

            # Otherwise return the error message received from the API
            else:
                return 'An error ocurred: ' + analytic.json()['message']

        # If we got an error through this process
        except:
            raise
            #return "An issue ocurred with calling the API"

    # Return the graphs to the call
    return graphs

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
