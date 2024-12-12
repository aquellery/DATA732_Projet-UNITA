import lecture_excel as le
import plotly.express as px
import pandas as pd

def normaliser_nom(nom):
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

def compter_occurences(dico, occurences):

    # Parcourir les éléments du dictionnaire
    for key, values in dico.items():
        for index, value in values.items():
            # Normaliser le nom
            nom_normalise = normaliser_nom(value)
            
            # Compter les occurrences des noms normalisés
            if nom_normalise in occurences:
                occurences[nom_normalise] += 1
            else:
                occurences[nom_normalise] = 1
    
    return occurences


#Camembert des répartitions des scopes
def camembert():
    dico=le.get_donnees_colonne('DISSEMINATION', ['SCOPE (Regional, National, European…)'])
    
    #On normalise l'ensemble des données
    normalised_data = {key: {k: normaliser_nom(v) for k, v in value.items()} for key, value in dico.items()}    

    occurences={}
    for key, values in normalised_data.items():
        for idx, value in values.items():
            if value in occurences:
                occurences[value] += 1
            else:
                occurences[value] = 1
            
    occurences=compter_occurences(dico, occurences)
    print(occurences)
    
    
    df=pd.DataFrame(list(occurences.items()), columns=['SCOPE', 'COUNT'])

    # Création du graphique en secteurs 
    fig = px.pie(df, values='COUNT', names='SCOPE', title='Differents scopes') 
    fig.show()
    
camembert()
    