import lecture_excel as le
import plotly.express as px
import pandas as pd

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
    
    
sc=scopes()
print(sc.get_event('Regional'))
#sc.camembert()
        