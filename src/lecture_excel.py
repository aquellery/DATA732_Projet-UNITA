import pandas as pd

file_name = '../data/data_entreprises.xlsx'  # File name

def get_feuilles(nom_feuille):
    #Le DataFrame du fichier excel
    df = pd.read_excel(file_name) 
    
    #passage DataFrame format Excel
    dico=df.to_dict()
    return dico

#print(get_feuilles('DISSEMINATION'))

def get_donnees_colonne(nom_feuille, nom_colonne):
    pass