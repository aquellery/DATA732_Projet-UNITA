import pandas as pd

file_name = 'data/data_entreprises.xlsx'  # File name

# ATTENTION : pour pouvoir récupérer des données il faut être sûre que le fichier Excel n'est pas ouvert
def get_feuilles(nom_feuille):
    #Le DataFrame du fichier excel
    df = pd.read_excel(file_name, nom_feuille) 
    
    #passage DataFrame format Excel
    dico=df.to_dict()
    return dico

def get_donnees_colonne(nom_feuille, liste_colonne):
    #On récupère des colonnes qui nous intéresse
    if(nom_feuille=="RIS"):
        df = pd.read_excel(file_name, nom_feuille, header=0) 
    elif (nom_feuille=="HUB"):
        df = pd.read_excel(file_name, nom_feuille, header=1) 
    elif (nom_feuille=="S3 Match"):
        df = pd.read_excel(file_name, nom_feuille, header=4)
    elif (nom_feuille=="TT & CI CONTACT"):
        df = pd.read_excel(file_name, nom_feuille, header=4)
    elif (nom_feuille=="UNIV - S3"):
        df = pd.read_excel(file_name, nom_feuille, header=3)
    elif (nom_feuille=="DISSEMINATION"):
        df = pd.read_excel(file_name, nom_feuille, header=4)
    elif (nom_feuille=="REGIONAL ECOSYSTEMS"):
        df = pd.read_excel(file_name, nom_feuille, header=3)
    elif (nom_feuille=="spinoffs contacts"):
        df = pd.read_excel(file_name, nom_feuille, header=5)      

    df_colonnes=df[liste_colonne]
    
    #passage DataFrame format Excel
    dico=df_colonnes.to_dict()
    return dico