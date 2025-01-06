import webbrowser
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import scopes as sc
import liste_contacts as lc
import proportion_universite_activite as pua
import proportion_entreprise_secteurs as pes
import map_uni_domains_companies as mudc

# Initialiser l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)


# Charger les graphiques au démarrage
print("Préchargement des graphiques...")
liste_contact = lc.afficher_liste_contacts()
print("Liste contacts préchargé")
figure_prop_ent = pes.afficher_prop_entreprise_secteurs()
print("Proportion entreprise préchargé")
figure_prop_uni = pua.afficher_prop_universite_activite()
print("Proportion universités préchargé")
scopes = sc.scopes(app)
figure_scopes = scopes.camembert()
print("Scopes préchargé")
all_data, df_companies, data_domain, centre_lat, centre_lon=mudc.get_all_data_map()
map=mudc.show_map(data_domain)
print("Map préchargée")

# Définir la disposition de l'application
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.H1(children='Tableau de bord interactif'),
    dcc.Dropdown(
        id='chart-type',
        options=[
            {'label': 'Vue globale', 'value': 'global'},
            {'label': 'Contacts', 'value': 'contacts'},
            {'label': 'Scopes', 'value': 'scopes'},
            {'label': 'Companies', 'value': 'entreprises'},
            {'label': 'Universities', 'value': 'univ'},
            {'label': 'Map of Univerties by Domain', 'value': 'map'}
        ],
        value='global'
    ),
    html.Div(id='graph-container'),
    html.Div(id='output-container'),

    # Add the map section as a placeholder
    html.Div([
        dcc.Dropdown(
        id='domain_choice',
        options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in data_domain],
        placeholder="Select a domain",
        multi=True
        ),
        dcc.Graph(id='map_display')
    ], id='map-container', style={'display': 'none'}),  # Initially hidden
])

# Définir le callback pour mettre à jour le graphique en fonction du type de graphique sélectionné
@app.callback(
    Output('graph-container', 'children'),
    [Input('chart-type', 'value')]
)

def update_graph(chart_type):
    if chart_type == 'contacts':
        print("Contacts sélectionné")
        return dcc.Graph(figure=liste_contact)
    elif chart_type == 'scopes':
        print("Scopes sélectionné")                
        return scopes.affichage_camembert(dcc)
    elif chart_type == 'entreprises':
        print("Entreprises sélectionné")
        return dcc.Graph(figure=figure_prop_ent)
    elif chart_type == 'univ':
        print("Univ sélectionné")
        return dcc.Graph(figure=figure_prop_uni)
    elif chart_type == 'global':
        print("Vue globale sélectionnée")
        # Liste des graphiques à afficher pour la vue globale
        graphs = [
            #html.Div(dcc.Graph(figure=figure_map_uni), style={'margin-bottom': '20px'}),
            html.Div(dcc.Graph(figure=figure_scopes), style={'margin-bottom': '20px'}),
            html.Div(dcc.Graph(figure=figure_prop_ent), style={'margin-bottom': '20px'}),
            html.Div(dcc.Graph(figure=figure_prop_uni), style={'margin-bottom': '20px'}),
        ]
        # Retourne la liste de graphiques pour la vue globale
        return html.Div(graphs, style={'display': 'block'})
    elif chart_type == 'map':
        print("Map sélectionné")
        return map
    
    return html.Div()  # Valeur par défaut si aucune sélection

scopes.register_callbacks()

if __name__ == '__main__':
    print("Lancement de l'application Dash DATA732")
    url="http://127.0.0.1:8051"
    webbrowser.open(url)
    app.run(debug=True, port=8051)