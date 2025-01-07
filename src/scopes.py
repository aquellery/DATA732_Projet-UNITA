import lecture_excel as le
import plotly.express as px
import pandas as pd
import dash_html_components as html
from dash.dependencies import Input, Output


class scopes:
    suppress_callback_exceptions=True
    
    def __init__(self, app) : 
        self.df=pd.DataFrame()
        self.app=app
    def normaliser_nom(self, nom):
        #Permet d'éviter certaines répétition : ne fonctionne certainement que pour quelques valeurs, il y a certainement des oublis dans la liste
        normalisation = {
            'from Local to International':'International',
            'all':'International' ,
            'regional, national' : 'Regional',
            'regional':'Regional',
            'national':'National',
            'N3' : 'National',
            'local' : 'Local'
        }
        return normalisation.get(nom,nom)

    def compter_occurences(self, dico, occurences):

        # Parcourir les éléments du dictionnaire
        for key, values in dico.items():
            for index, value in values.items():
                # Normaliser le nom
                nom_normalise = self.normaliser_nom(value)
                
                # Compter les occurrences des noms normalisés
                if nom_normalise in occurences:
                    occurences[nom_normalise] += 1
                else:
                    occurences[nom_normalise] = 1
        
        return occurences


    #Camembert des répartitions des scopes
    def camembert(self):
        dico=le.get_donnees_colonne('DISSEMINATION', ['SCOPE (Regional, National, European…)'])
        
        #On normalise l'ensemble des données
        normalised_data = {key: {k: self.normaliser_nom(v) for k, v in value.items()} for key, value in dico.items()}    

        occurences={}
        for key, values in normalised_data.items():
            for idx, value in values.items():
                if value in occurences:
                    occurences[value] += 1
                else:
                    occurences[value] = 1
                
        occurences=self.compter_occurences(dico, occurences)
        print(occurences)
        
        self.df=pd.DataFrame(list(occurences.items()), columns=['SCOPE', 'COUNT'])

        # Création du graphique en secteurs 
        fig = px.pie(self.df, values='COUNT', names='SCOPE', title='Differents scopes') 
        return fig 
    
    def get_df(self):
        return self.df
    
    def get_event(self, type_event):
        #type-event : Regional, National, International, Local
        event={'SCOPE (Regional, National, European…)': [], 'PARTNER (select)':[],'DISSEMINATION ACTIVITY NAME':[]}
        dico=le.get_donnees_colonne('DISSEMINATION', ['PARTNER (select)','DISSEMINATION ACTIVITY NAME','SCOPE (Regional, National, European…)'])
        
        #On normalise l'ensemble des données
        normalised_data = {key: {k: self.normaliser_nom(v) for k, v in value.items()} for key, value in dico.items()}    

        for i in range(len(dico['SCOPE (Regional, National, European…)'])):
            print(f"Index: {i}, Scope: {normalised_data['SCOPE (Regional, National, European…)'][i]}")
            if normalised_data['SCOPE (Regional, National, European…)'][i] == type_event:
                event['SCOPE (Regional, National, European…)'].append(normalised_data['SCOPE (Regional, National, European…)'][i])
                event['PARTNER (select)'].append(normalised_data['PARTNER (select)'][i])
                event['DISSEMINATION ACTIVITY NAME'].append(normalised_data['DISSEMINATION ACTIVITY NAME'][i])
        event_list = list(zip(event['SCOPE (Regional, National, European…)'], event['PARTNER (select)'], event['DISSEMINATION ACTIVITY NAME']))
        return event_list
    
    def affichage_camembert(self, dcc):
        return html.Div([
            dcc.Graph(
                id='pie-chart',
                figure=self.camembert()
            ),
            html.Div(id='event-list')
        ])

    def register_callbacks(self):
        @self.app.callback(
            Output('event-list', 'children'),
            [Input('pie-chart', 'clickData')]
        )
        def display_events(clickData):
            if clickData is None:
                return "Click on a part of the graph to see the associated events."
            else:
                try:
                    scope = clickData['points'][0]['label']
                    print(f"Nom de la part cliquée: {scope}")
                    infos = self.get_event(scope)
                    print(infos)
                    items = [html.Li(f"The partner {assoc_scope[1]} took part in {assoc_scope[2]}") for assoc_scope in infos]
                    return html.Div([
                        html.P(f"Events associated with the scope  {scope}:"),
                        html.Ul(items),
                        html.Br(),  # Ajout d'un retour à la ligne
                        html.P("Click on another part of the graph to see more events.")
                    ])
                except Exception as e:
                    print(f"Erreur: {e}")
                    return "Erreur lors de la récupération des scopes associés."