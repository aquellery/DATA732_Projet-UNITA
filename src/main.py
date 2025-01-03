import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import scopes as sc

# Initialiser l'application Dash
app = dash.Dash(__name__)

sc=sc.scopes()
fig=sc.camembert()
df=sc.get_df()

app.layout = html.Div([
    dcc.Graph(
        id='pie-chart',
        figure=fig
    ),
    html.Div(id='event-list')
])

@app.callback(
    Output('event-list', 'children'),
    [Input('pie-chart', 'clickData')]
)

def display_events(clickData):
    '''
    Récupère des données sous la forme {'points':
    [{'curveNumber': 0, 'label': 'Regional', 'color': '#EF553B', 'value': 32, 
    'percent': 0.2909090909090909, 'v': 32, 'i': 1, 'pointNumber': 1, 
    'bbox': {'x0': 456.17786237470426, 'x1': 575.5, 'y0': 137.33337260379534, 'y1': 256.65551022909113}, 
    'pointNumbers': [1]}]}
    '''
    if clickData is None:
        return "Cliquez sur une part du graphique pour voir les événements associés."
    else:
        try:
            scope = clickData['points'][0]['label']
            print(f"Nom de la part cliquée: {scope}")
            infos = sc.get_event(scope)
            print(infos)
            items = [html.Li(f"Le partenaire {assoc_scope[1]} a participé à {assoc_scope[2]}") for assoc_scope in infos]
            return html.Div([
                html.P(f"Evénements associés au scope {scope}:"),
                html.Ul(items),
                html.Br(),  # Ajout d'un retour à la ligne
                html.P("Cliquez sur une autre part du graphique pour voir plus d'événements.")
            ])
        except Exception as e:
            print(f"Erreur: {e}")
            return "Erreur lors de la récupération des scopes associés."

if __name__ == '__main__':
    app.run_server(debug=True)