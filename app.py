from dash import Dash, dcc, html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import glob
#-------------------------------------------------------------------------------
csv_f = glob.glob('data_f/*.csv')
df_list = (pd.read_csv(file,sep=';',encoding='ANSI') for file in csv_f)

data = pd.concat(df_list, ignore_index = True)
data['Datum'] = pd.to_datetime(data.Datum, format='%Y-%m-%d')

Besigheid= data['Besigheid'].unique()      
Besigheid.sort()
#-------------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = html.Div ([
    html.Br(),
    html.H1("Gansbaai Heuning",style={'textAlign':'center'}),
    html.Br(),
    html.Div([
        dcc.Tabs([
            dcc.Tab(
                label='Over the Years',
                children=[
                html.Div([
                    dcc.Dropdown(id='be_Drop',
                        options=[{'label':besigheid, 'value':besigheid}
                            for besigheid in Besigheid]),
                ],
                style={
                    'width': '25%',
                    'paddingLeft':'48px',
                    'paddingTop':'5px'},
                ),
                html.Div([
                    dbc.Button('Go',id='Button',),
                ],
                style={
                    'paddingLeft':'50px',
                    'paddingTop':'4px'}
                ),
                html.Br(),
                html.Div(
                    id='graph_container',
                    children=[
                    dcc.Loading([
                        dcc.Graph(id='barfig'), 
                    ])
                ],style={'width':'70%'}
                ),
            ]),
            
            dcc.Tab(
                label='Opsomming',
                children=[
                html.Div([
                    dcc.Dropdown(id='be_Drop2',
                    options=[{'label':besigheid, 'value':besigheid}
                        for besigheid in Besigheid])
                ],
                style={
                    'width': '25%',
                    'paddingLeft':'48px',
                    'paddingTop':'5px'},
                ),
                html.Br(),
                html.Div(
                    id='table',
                    children=[],
                    style={
                    'width': '70%',
                    'paddingLeft':'25%',
                    }

                )
            ])
        ]),
    ])
])

#-------------------------------------------------------------------------------
@app.callback(Output('table','children'),
                Input('be_Drop2','value'))
def make_Table(besigheid):
    if not besigheid:
        raise PreventUpdate
    df2 = []
    df3 = []
    BisTab2 = data.loc[data['Besigheid']==besigheid]
    start = BisTab2['Datum'].iloc[0].year
    stop =  BisTab2['Datum'].iloc[-1].year
    
    for year in range(start,stop+1):
        df2.append(BisTab2[BisTab2['Datum'].isin(
            pd.date_range('{}-01-01'.format(year),'{}-12-31'.format(year)))
        ])
    for i in df2:
        df3.append( html.Div(dbc.Table.from_dataframe(i)))
        df3.append(html.Br())
        df3.append(html.Div('Total: R {:.2f}'.format(i.Bedrag.sum())))
        df3.append(html.Br())
    return df3

#-------------------------------------------------------------------------------
@app.callback(Output('graph_container','style'),Input('Button','n_clicks'))
def hide(n_clicks):
    if n_clicks:
        return {'display':'block'}
    return {'display':'none'}

#-------------------------------------------------------------------------------
@app.callback(Output('barfig','figure'),
                Input('Button','n_clicks'),
                State('be_Drop','value'),)
def make_plot(n_clicks,besigheid):
    if not n_clicks:
        raise PreventUpdate

    Bis = data.loc[data['Besigheid']==besigheid]
    start = Bis['Datum'].iloc[0].year
    stop =  Bis['Datum'].iloc[-1].year
    Bis = Bis.groupby(pd.Grouper(key='Datum',freq='MS')).sum()
    
    dates = pd.date_range('{}-01'.format(start),'{}-12'.format(stop), freq='MS')
    df = pd.DatetimeIndex.to_frame(dates,name = 'Datum')

    df['Bedrag'] = Bis['Bedrag']
    df['Month'],df['Year'] = df['Datum'].dt.month, df['Datum'].dt.year
    df['Month'] = pd.to_datetime(df['Month'], format='%m').dt.month_name().str.slice(stop=3)
    
    fig= px.histogram(df,x ='Month', y = 'Bedrag', barmode='group',color='Year')
    fig.update_layout(
        title = '{} Total per Month'.format(besigheid),
        title_x = 0.5,
        yaxis_title='Total: R',)
    
    fig.layout.xaxis.tickformat = '%b'
    return fig
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)