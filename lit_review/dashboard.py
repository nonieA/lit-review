import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# import data

data = pd.read_csv('data/processed/litreview_analysis.csv')
short = data.drop_duplicates('Title')
country_df = short['Country'].value_counts().reset_index().rename(columns={'index':'Country','Country':'Count'})
country_df.loc[country_df['Country']=='USA','Country']='United States'
country_df.loc[country_df['Country']=='UK','Country']='United Kingdom'

df = px.data.gapminder().query("year==2007")
country_df = pd.merge(df[['country','iso_alpha']],country_df, how = 'right',left_on='country',right_on='Country')
country_df.loc[3,'country'] = 'Russia'
country_df.loc[3,'iso_alpha'] = 'RUS'
country_df.loc[5,'country'] = 'South Korea'
country_df.loc[5,'iso_alpha'] = 'KOR'
country_plot = px.choropleth(country_df, locations="iso_alpha",
                    color="Count", # lifeExp is a column of gapminder
                    hover_name="Country", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma)

# app layout

app.layout = html.Div([

    html.H1('Interactive Scoping Review', style={'text-align':'left',
          "backgroundColor":"#F0e7E2"}),

    html.Div([
        html.H3('Study Context'),

        html.Div([
            html.H4('Research area and year of study'),

            dcc.Dropdown(id="study_con",value='Disease',
                         options=[
                            {"label":'Publication Year', "value":'Year'},
                            {"label":'Research Area', "value":'Disease'}
                         ]),

            html.Br(),

            dcc.Graph(
                id='st_plt'
        ),
        ]),

        html.Br(),

        html.Div([
            html.H4('Health Care Setting'),

            dcc.Dropdown(id="set_type",value='cohort',
                         options=[
                            {"label":'Time type: All', "value":'all'},
                            {"label":'Time type: Non-temporal', "value":'cohort'},
                            {"label":'Time type: Temporal', "value":'longitudinal'}
                         ]
                         ),

            html.Br(),

            dcc.Graph(id='setting',style={
                  "background-color":"#F0e7E2"}),

            html.Br()
        ],style={'width':'33%','display':'inline-block'}),

        html.Div([
            html.H4('Country of data'),
            html.Br(),
            dcc.Graph(id='country_plot',figure=country_plot,style={
                  "backgroundColour":"#F0e7E2"})
            ],style={'width':'50%','display':'inline-block','align':'right'})

    ], id = 'study_context')

], style={"font-family":"verdana",
          "background-color":"#F0e7E2"})

# plots

@app.callback(
    Output(component_id='st_plt', component_property='figure'),
    Output(component_id='setting', component_property='figure'),
    Input(component_id='study_con', component_property='value'),
    Input(component_id='set_type', component_property='value')
)

def stud_plot(stud_var,set_type):

    disease_df = data.drop_duplicates(['Title', stud_var])[stud_var].value_counts().reset_index().rename(columns={
        'index': stud_var,
        stud_var: 'Number of Studies'}).sort_values(stud_var)
    disease_df['colour'] = [str(i % 4) for i in range(len(disease_df))]
    disease_plot = px.bar(disease_df, x=stud_var, y='Number of Studies', color='colour',
                          color_discrete_sequence=['#D90368', '#197278', '#541388', '#F18805'])
    disease_plot.update_layout(
        showlegend=False, xaxis=go.layout.XAxis(
            tickangle=-60),
        plot_bgcolor="#F0e7E2",
        font=dict(size=14)
    )
    if stud_var == 'Disease':
        disease_plot.update_xaxes(categoryorder='category ascending')

    if set_type == 'all':
        care_df = short['Primary or Secondary Care'].value_counts().rename({
            'Primary or Secondary Care': 'Count'
        })
    else:
        care_df = short[short['Time Type']==set_type]['Primary or Secondary Care'].value_counts().rename({
            'Primary or Secondary Care': 'Count'
        })

    if 'Tertiary' in care_df.index:
            care_df['Secondary'] = care_df['Secondary'] + care_df['Tertiary']

    p_d = care_df.loc['Primary'] + care_df.loc['Both']
    s_d = care_df.loc['Secondary'] + care_df.loc['Both']
    b_d = care_df.loc['Both']
    s_w = s_d / p_d
    b_w = b_d / p_d

    p_x0 = 0
    p_x1 = 1
    p_y0 = 0
    p_y1 = 1

    s_x0 = 1 - b_w
    s_x1 = s_x0 + s_w
    s_y0 = 0.5 - s_w / 2
    s_y1 = 0.5 + s_w / 2

    fig = go.Figure()

    # Create scatter trace of text labels
    fig.add_trace(go.Scatter(
        x=[p_x1 / 3 - 0.1, s_x1 / 2 - 0.1, s_x1 - s_w / 3],
        y=[0.5, 0.5, 0.5],
        text=[i + '<br>' + str(care_df.loc[i]) + ' papers' if i == 'Both' else i + ' care<br>' + str(
            care_df.loc[i]) + ' papers' for i in ["Primary", "Both", "Secondary"]],
        mode="text",
        textfont=dict(
            color="black",
            size=13,
            family="Arial",
        )
    ))

    # Update axes properties
    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    # Add circles
    fig.add_shape(type="circle",
                  line_color='#541388', fillcolor='#541388',
                  x0=p_x0, y0=p_y0, x1=p_x1, y1=p_y1
                  )
    fig.add_shape(type="circle",
                  line_color='#197278', fillcolor='#197278',
                  x0=s_x0, y0=s_y0, x1=s_x1, y1=s_y1
                  )
    fig.update_shapes(opacity=0.3, xref="x", yref="y")

    fig.update_layout(
        margin=dict(l=20, r=20, b=100),
        height=390, width=300,
        plot_bgcolor="white"
    )

    return disease_plot,fig



if __name__ == '__main__':
    app.run_server(debug=False)


