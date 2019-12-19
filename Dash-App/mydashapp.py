import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from preprocess import preprocess, merge
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

exercise = pd.read_csv('./Exercise.csv')
sleep = pd.read_csv('./sleep.csv')
steps = pd.read_csv('./step_count.csv')
steps_daily = pd.read_csv('./step_daily_trend.csv')
calories = pd.read_csv('./calories_burned.csv')
stress = pd.read_csv('./stress.csv')
heart_rate = pd.read_csv('./heart_rate.csv')


exercise = preprocess(exercise)
sleep = preprocess(sleep, True, True)
steps = preprocess(steps, False, True)
steps_daily = preprocess(steps_daily, True, False)
calories = preprocess(calories)
stress = preprocess(stress)
heart_rate = preprocess(heart_rate)

df_list = [sleep, exercise, calories, stress, steps, heart_rate]
merged_df = merge(df_list)

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H1('Health Project'),
    html.P('By: Ahmed Al-Baz'),
    dcc.Tabs(id = "Metrics", value = "tabs-1", children = [
        dcc.Tab(label = 'Exercise', value = 'tabs-1'),
        dcc.Tab(label = 'Sleep', value = 'tabs-2'),
        dcc.Tab(label = 'Step Count', value = 'tabs-3'),
        dcc.Tab(label = 'Calories', value = 'tabs-4'),
        dcc.Tab(label = 'Stress', value = 'tabs-5'),
        dcc.Tab(label = 'Correlations', value = 'tabs-6')
    ]),
    html.Div(id = 'test-run')
])

@app.callback(Output('test-run', 'children'),
                [Input('Metrics', 'value')])

def render_content(tab):
    if tab == 'tabs-1':
        pv = exercise.groupby(['date', 'weekday', 'exercise_type'], as_index = False)['duration'].sum()
        pv2 = pd.pivot_table(pv, index = ['weekday'], columns = ['exercise_type'], values = ['duration'], aggfunc = np.median, fill_value = 0)
        fig = go.Figure(data=[
                go.Bar(name = 'Brisk Walking', x = pv2.index, y = pv2[('duration', 'Brisk Walking')]),
                go.Bar(name = 'Circuit Training', x = pv2.index, y = pv2[('duration', 'Circut Training')]),
                go.Bar(name = 'Custom', x = pv2.index, y = pv2[('duration', 'Custom')]),
                go.Bar(name = 'Elliptical', x = pv2.index, y = pv2[('duration', 'Elliptical')]),
                go.Bar(name = 'Hiking', x = pv2.index, y = pv2[('duration', 'Hiking')]),
                go.Bar(name = 'Running', x = pv2.index, y = pv2[('duration', 'Running')]),
                go.Bar(name = 'Swimming', x = pv2.index, y = pv2[('duration', 'Swimming')]),
                go.Bar(name = 'Walking', x = pv2.index, y = pv2[('duration', 'Walking')])
                ])
        fig.update_layout(
            title='<b>Daily Median Exercise Duration (By Day of the Week)</b>',
            xaxis=dict(
            title = '<b>Day of the Week</b>',
            tickfont_size=14,
            ),
            yaxis=dict(
            title='<b>Duration (minutes)</b>',
            titlefont_size=16,
            tickfont_size=14,
            )
            )
        return html.Div([
            html.H3('Exercise'),
            dcc.Graph(
                id = 'Exercise Graph',
                figure = fig
        )
        ])
    elif tab == 'tabs-2':
        return html.Div([
            html.H3('Sleep'),
            dcc.Dropdown(id = 'Sleep-Dropdown',
                options=[
                    {'label': 'Bedtime Hours', 'value': 'start_hour'},
                    {'label': 'Wakeup Hours', 'value': 'end_hour'},
                    {'label': 'Durations (Hours)', 'value': 'duration'}
                        ],
                value = 'start_hour',
                searchable=False
                        ),  
            dcc.Graph(
                id = 'Sleep-Graph',
        )])
    elif tab == 'tabs-3':
        pv = pd.pivot_table(steps_daily, index = ['create_time'], columns = ['deviceuuid'], values = ['count'], aggfunc = sum, fill_value = 0)
        fig = go.Figure()

        for element in steps_daily['deviceuuid'].unique():
            fig.add_trace(go.Scatter(x = pv.index, y = pv[('count', element)], mode = 'lines', name = element, connectgaps = True))

        fig.update_layout(
            title='<b>Daily Step Count(By Device)</b>',
            xaxis=dict(
            title = '<b>Date</b>',
            tickfont_size=14,
            ),
            yaxis=dict(
            title='<b>Step Count</b>',
            titlefont_size=16,
            tickfont_size=14,
            )
            )
        pv2 = steps.groupby(['date', 'day_label', 'create_hour'], as_index = False)['count'].sum()
        pv2 = pd.pivot_table(pv2, index = ['create_hour'], columns = ['day_label'], values = ['count'], aggfunc = np.median, fill_value = 0)
        fig2 = go.Figure()

        for element in steps['day_label'].unique():
            fig2.add_trace(go.Bar(x = pv2.index, y = pv2[('count', element)], name = element))

        fig2.update_layout(
            title='<b>Hourly Median Step Count(By Weekend/Weekday)</b>',
            xaxis=dict(
            title = '<b>Hour of the Day</b>',
            tickfont_size=14,
            tick0 = 0,
            dtick = 1,
            ),
            yaxis=dict(
            title='<b>Step Count</b>',
            titlefont_size=16,
            tickfont_size=14,
            )
            )
        return html.Div([
            html.H3('Step Count'),
            dcc.Graph(
                id = 'Step Count Graph',
                figure= fig
            ),
            dcc.Graph(
                id = 'Step Count Hourly',
                figure = fig2
            )
        ])
    elif tab == 'tabs-4':
        pv = pd.pivot_table(calories, index = ['create_time'], values = ['active_calorie', 'rest_calorie'], aggfunc = np.median, fill_value = 0)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x = list(pv.index), y = list(pv.active_calorie), name = 'active_calorie')
        )
        fig.add_trace(
            go.Scatter(x = list(pv.index), y= list(pv.rest_calorie), name = 'rest_calorie')
        )
        fig.update_layout(
            title = 'Rest and Active Calories (kcal)',
            xaxis = go.layout.XAxis(
                title = '<b>Date</b>',
                rangeselector = dict(
                    buttons = list([
                        dict(count = 1, label = '1m', step = 'month', stepmode = 'backward'),
                        dict(count = 3, label = '3m', step = 'month', stepmode = 'backward'),
                        dict(count = 6, label = '6m', step = 'month', stepmode = 'backward'),
                        dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
                        dict(count = 1, label = '1y', step = 'year', stepmode = 'backward'),
                        dict(label = 'ALL', step = 'all')])
                ),
                rangeslider = dict(visible = True),
                type = 'date'
                    ),
            yaxis = dict(
                title='<b>Calories (kcal)</b>',
                titlefont_size=16,
                tickfont_size=14)
            )
        return html.Div([
            html.H3('Calories'),
            dcc.Graph(
                id = 'Calories Graph',
                figure = fig
        )
        ])
    elif tab == 'tabs-5':
        fig = go.Figure()
        fig.add_trace(
            go.Box(x = stress['weekday'], y = stress['score'])
        )
        fig.update_layout(
            title = '<b>Stress Score Distribution (By Weekday)</b>',
            xaxis = dict(
                title = '<b>Day of the Week</b>'
            ),
            yaxis = dict(
                title = '<b>Stress Score</b>'
            )
        )
        return html.Div([
            html.H3('Stress'),
            dcc.Graph(
                id = 'Stress Graph',
                figure= fig
        )
        ])
    elif tab == 'tabs-6':
        z = merged_df.corr().values
        z_text = np.round(z, decimals = 2)
        fig = ff.create_annotated_heatmap(z, x = list(merged_df.columns[1:]), y = list(merged_df.columns[1:]), annotation_text = z_text, showscale = True)
        fig.update_layout(
            title = '<b>Correlation Matrix Heatmap for Health Data Features</b>'
            )
        return html.Div([
            html.H3('Correlations'),
            dcc.Graph(
                id = 'Correlations Graph',
                figure= fig
        )
        ])

@app.callback(Output('Sleep-Graph', 'figure'),
                [Input('Sleep-Dropdown', 'value')])

def update_sleep_graph(selection_value):
    fig = go.Figure(data = [
        go.Histogram(x = sleep[str(selection_value)], 
                    histnorm = 'probability', nbinsx = 24)
    ])
    labels_dict = {'start_hour': 'Bedtime Hours', 'end_hour': 'Wakeup Hours', 'duration': 'Sleep Duration (Hours)'}
    fig.update_layout(
            title='<b>Distribution of ' + labels_dict[str(selection_value)]+'</b>',
            xaxis=dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1,
            title = "<b>" + labels_dict[str(selection_value)] + "</b>",
            titlefont_size=16,
            tickfont_size=14
            ),
            yaxis=dict(
            title='<b>Frequency</b>',
            titlefont_size=16,
            tickfont_size=14
        ))
    return fig

if __name__ == '__main__':
    app.run_server(debug = True)
