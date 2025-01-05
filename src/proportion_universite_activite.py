import pandas as pd
import plotly.express as px
from lecture_excel import get_donnees_colonne

# Fonction pour traiter les cas où plusieurs universités sont mentionnées
def map_multiple_partners(partner_value):
    # Nettoyer les espaces et uniformiser la casse 
    if isinstance(partner_value, str):
        partner_value = partner_value.strip()  # Supprimer les espaces 

        # Normaliser "Mont Blanc" et "Savoie Mont Blanc" sans tiret
        partner_value = partner_value.replace("Mont Blanc", "Mont-Blanc")  # Remplacer Mont Blanc sans tiret par avec tiret
        partner_value = partner_value.replace("de Savoie", "Savoie")

    return [partner_value]  # Si c'est une seule université, on retourne directement la valeur

# Utilisation de la fonction pour extraire la colonne "PARTNER (select)" de la feuille "Dissemination"
nom_feuille = "DISSEMINATION"
liste_colonne = ["PARTNER (select)"]  # Nom de la colonne ciblée
dico = get_donnees_colonne(nom_feuille, liste_colonne)

# Extraire la colonne des partenaires sous forme de série
partners = pd.Series(dico["PARTNER (select)"])

# Appliquer la fonction de mappage des partenaires multiples
all_partners = []

for partner_value in partners:
    mapped_partners = map_multiple_partners(partner_value)
    all_partners.extend(mapped_partners)  # Ajouter tous les partenaires mappés

# Créer une nouvelle série avec tous les partenaires correctement mappés
partners_categorises = pd.Series(all_partners)

# Compter les occurrences de chaque partenaire (université)
partners_count = partners_categorises.value_counts().reset_index()
partners_count.columns = ["Université", "Nombre"]

# Création du pie chart avec Plotly
def afficher_prop_universite_activite():
    fig = px.pie(partners_count, names="Université", values="Nombre", title="Proportions des universités dans 'PARTNER (select)'")
    return fig
    #fig.show()
