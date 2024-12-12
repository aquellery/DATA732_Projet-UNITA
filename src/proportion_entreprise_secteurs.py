import pandas as pd
import plotly.express as px
from lecture_excel import get_donnees_colonne

# Définir le chemin du fichier Excel
file_name = '../Data/data_entreprises.xlsx'  # File name

# Définir le nom de la feuille et la colonne à extraire
nom_feuille = "spinoffs contacts"
liste_colonne = ["S3 LINKED SECTOR (Select)"]

# Appeler la fonction pour récupérer les données
donnees_secteurs = get_donnees_colonne(file_name, nom_feuille, liste_colonne)

# Afficher les données récupérées
print(donnees_secteurs)

# Extraire les données de la colonne 'S3 LINKED SECTORS (Select)'
secteurs_data = donnees_secteurs['S3 LINKED SECTOR (Select)']

# Compter les occurrences des secteurs
sector_counts = pd.Series(secteurs_data).str.split(',').explode().str.strip().value_counts()

# Calculer les proportions
total = sector_counts.sum()
sector_proportions = (sector_counts / total) * 100

# Créer un Pie Chart avec Plotly
fig = px.pie(
    names=sector_proportions.index,
    values=sector_proportions.values,
    title="Répartition des secteurs (S3 LINKED SECTORS)"
)

# Afficher le graphique
fig.show()
