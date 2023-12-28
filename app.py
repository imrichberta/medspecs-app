import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
import plotly.graph_objects as go

# Categories list
categories = [
    'Infekčné a parazitárne choroby ( A00 - B99 )',
    'Nádory ( C00 - D48 )',
    'Choroby krvi a krvotvorných orgánov a niektoré poruchy s účasťou imunitných mechanizmov ( D50 - D90 )',
    'Endokrinné, nutričné a metabolické choroby ( E00 - E90 )',
    'Duševné poruchy a poruchy správania ( F00 - F99 )',
    'Choroby nervovej sústavy ( G00 - G99 )',
    'Choroby oka a očných adnexov ( H00 - H59 )',
    'Choroby ucha a hlávkového výbežku ( H60 - H95 )',
    'Choroby obehovej sústavy ( I00 - I99 )',
    'Choroby dýchacej sústavy ( J00 - J99 )',
    'Choroby tráviacej sústavy ( K00 - K93 )',
    'Choroby kože a podkožného tkaniva ( L00 - L99 )',
    'Choroby svalovej a kostrovej sústavy a spojivového tkaniva ( M00 - M99 )',
    'Choroby močovopohlavnej sústavy (N00-N99)',
    'Gravidita, pôrod a šestonedelie ( O00 - O99 )',
    'Subjektívne a objektívne príznaky, abnormálne klinické a laborat. nálezy,nezatriedené inde  (R00 - R99)',
    'Poranenia, otravy a niektoré iné následky vonkajších príčin ( S00 - T98 )',
    'Vrodené chyby, deformity a chromozómové anomálie ( Q00 - Q99)',
    'Kódy na osobitné účely ( U00 - U99 )',
    'Vonkajšie príčiny chorobnosti a úmrtnosti ( V01 - Y98 )',
    'Faktory ovplyvňujúce zdravotný stav a styk so zdravotníckymi službami ( Z00 - Z99 )'
]

# Assigning colors
colors = [
    '#FF6347',  # Tomato
    '#4682B4',  # SteelBlue
    'darkred',  # LimeGreen
    'orange',  # Gold
    '#6A5ACD',  # SlateBlue
    '#FF69B4',  # HotPink
    '#7FFFD4',  # Aquamarine
    '#D2691E',  # Chocolate
    'red',  # CornflowerBlue
    '#008080',  # Teal
    '#DC143C',  # Crimson
    '#008B8B',  # DarkCyan
    '#B8860B',  # DarkGoldenRod
    '#9932CC',  # DarkOrchid
    '#8FBC8F',  # DarkSeaGreen
    'pink',
    'purple',
    '#483D8B',  # DarkSlateBlue
    '#2F4F4F',  # DarkSlateGray
    '#00CED1',  # DarkTurquoise
    '#9400D3',  # DarkViolet
]

# Creating a DataFrame
cis_col = pd.DataFrame({'kap': categories, 'color': colors})

stats_odb=pd.read_excel('./data/stats_odb.xlsx')
stats_odb['ozou_kod']=stats_odb.ozou_ksp.str[0:3]

pac_dgn_vcn = pd.read_excel('./data/stats_dgn.xlsx')

pac_dgn_vcn = pac_dgn_vcn[pac_dgn_vcn.mkch10_3_kod!='!'].reset_index(drop=True)
pac_dgn_vcn['kap']=pac_dgn_vcn.mkch10_kap_pop.str.split('o l a - ',expand=True)[1]
pac_dgn_vcn=pac_dgn_vcn.merge(cis_col,how='left',on='kap')

if pac_dgn_vcn.ozou_kod.dtype==int:
    pac_dgn_vcn['ozou_kod']=pac_dgn_vcn.ozou_kod.astype(str).str.zfill(3)
    
    
sel_odb=['001','002','003','004','005','008','009',
         '010','011','012','014','015','018','019',
         '020','023','025','027','029','031','034',
         '037','038','040','045','048','049','050','069']


import dash
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)


# App layout
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': stats_odb.loc[stats_odb.ozou_kod==key,'ozou_ksp'].iloc[0], 'value': key} for key in sel_odb],
        value='020'  # default value
    ),
        dcc.Graph(
        id='bar-plot',
        style={'height': '100vh'}  # Set the height of the graph to 100% of the viewport height
    )
], style={'height': '100vh'}) 

# Callback to update bar-plot based on dropdown selection
@app.callback(
    Output('bar-plot', 'figure'),
    [Input('dropdown', 'value')]
)
def update_graph(odb):
    
    data_plot = pac_dgn_vcn.query('ozou_kod=="'+odb+'"')
    data_plot = data_plot[(data_plot.vcn>5e-3)]
    data_plot = data_plot.sort_values('mkch10_3_kod')
    data_plot['text_size'] = (data_plot['vcn']**(1/3) )*100
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
            x=data_plot.mkch10_3_kod,
            y=data_plot.vcn,
            name='mkch',width=(data_plot['vcn']**(1/3) )*5,
            marker_color=data_plot['color'],opacity=0.2
        ))
    '''
    fig.add_trace(go.Scatter(
            x=data_plot.mkch10_3_kod,
            y=data_plot.vcn,
            name='mkch',
        mode='markers',opacity=0.7,
            marker=dict(
                size=data_plot['vcn'] * 2000,  # Adjust the size as needed
                color=data_plot['color']
            )
        ))
    '''
    mask=data_plot.text_size>1
    fig.add_trace(go.Scatter(
            x=data_plot[mask].mkch10_3_kod,
            y=data_plot[mask].vcn,
            name='mkch',
        mode='text',
        text=data_plot[mask]['ksp'],  # The text to display (same as value here)
            textposition="middle center",
            textfont=dict(  # Set the text font size
                size=(data_plot[mask]['text_size']/3).tolist(),
                color=data_plot[mask]['color']
            )
        ))
    fig.update_layout(
        title='Najčastejšie dôvody ambulantných návštev, odb: '+odb,
        xaxis_title='MKCH10',
        yaxis_title='Pomer pacientov',
        barmode='group',
        paper_bgcolor='white',  # Set the background of the whole figure to white
        plot_bgcolor='white',    # Set the background of the plotting area to white
            showlegend=False       # Remove the legend

    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False,port=8080)