import lecture_excel as le
import plotly.express as px
import pandas as pd
import dash_html_components as html

class scopes:
    
    def __init__(self) : 
        self.df=pd.DataFrame()
    
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
    
        
    
sc=scopes()
print(sc.get_event('Regional'))
#sc.camembert()

