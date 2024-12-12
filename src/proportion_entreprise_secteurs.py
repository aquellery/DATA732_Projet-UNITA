import pandas as pd
import plotly.express as px

# Charger le fichier Excel
file_path = "Data\data_entreprises.xlsx"  # Remplacez par le chemin de votre fichier
sheet_name = "spinoffs contacts"

# Lire les données de la feuille
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Accéder à la colonne "S3 LINKED SECTORS (Select)"
column_name = "S3 LINKED SECTOR (Select)"
data = df[column_name].dropna()  # Supprimer les valeurs manquantes

# Compter les occurrences des secteurs
sector_counts = data.str.split(',').explode().str.strip().value_counts()

# Calculer les proportions
total = sector_counts.sum()
sector_proportions = (sector_counts / total) * 100

# Créer un Pie Chart avec Plotly
fig = px.pie(
    names=sector_proportions.index,
    values=sector_proportions.values,
    title="Répartition des secteurs (S3 LINKED SECTOR)"
)

# Afficher le graphique
fig.show()
