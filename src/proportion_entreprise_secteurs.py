import pandas as pd
import plotly.express as px
from lecture_excel import get_donnees_colonne

# Mappage des secteurs pour les regrouper dans les catégories principales
sector_mapping = {
    'TOURISM': 'TOURISM',
    'DIGITAL & CREATIVE INDUSTRIES': 'DIGITAL & CREATIVE INDUSTRIES',
    'AGRO': 'AGRO',
    'AUTOMOTIVE / MOBILITY': 'AUTOMOTIVE / MOBILITY',
    'HEALTH / LIFE SCIENCES': 'HEALTH / LIFE SCIENCES',
    'FORESTRY / ECOLOGY / SUSTAINABILITY': 'FORESTRY / ECOLOGY / SUSTAINABILITY',
    'BIOTECH': 'BIOTECH',
    'ENERGY': 'ENERGY',
    'MANUFACTURING': 'MANUFACTURING',
    'AEROSPACE': 'AEROSPACE',
    'TEXTILE': 'TEXTILE',
    'OTHER': 'OTHER',
    'Entrepreneurship': 'Entrepreneurship',
    
    # Ajout des variations à regrouper sous les catégories principales
    'ENERGY EFFICIENCY': 'ENERGY',
    'ENERGY ': 'ENERGY'
}

# Fonction pour traiter les cas où plusieurs secteurs sont mentionnés
def map_multiple_sectors(sector_value):
    # Si la valeur contient un point-virgule, elle représente plusieurs secteurs
    if isinstance(sector_value, str) and ';' in sector_value:
        sectors = sector_value.split(';')  # Divise la chaîne sur le point-virgule
        mapped_sectors = []
        for sector in sectors:
            sector = sector.strip()  # Enlève les espaces superflus
            # Si le secteur est dans le mappage, on l'ajoute
            if sector in sector_mapping:
                mapped_sectors.append(sector_mapping[sector])
            else:
                mapped_sectors.append('OTHER')  # Si ce n'est pas dans le mappage, on met 'OTHER'
        return mapped_sectors
    # Sinon, on mappe normalement
    return [sector_mapping.get(sector_value, 'OTHER')]

# Utilisation de la fonction pour extraire la colonne
nom_feuille = "spinoffs contacts"
liste_colonne = ["S3 LINKED SECTOR (Select)"]  # Nom de la colonne ciblée
dico = get_donnees_colonne(nom_feuille, liste_colonne)

# Extraire la colonne des secteurs sous forme de série
secteurs = pd.Series(dico["S3 LINKED SECTOR (Select)"])

# Appliquer la fonction de mappage des secteurs multiples
all_sectors = []

for sector_value in secteurs:
    mapped_sectors = map_multiple_sectors(sector_value)
    all_sectors.extend(mapped_sectors)  # Ajouter tous les secteurs mappés

# Créer une nouvelle série avec tous les secteurs correctement mappés
secteurs_categorises = pd.Series(all_sectors)

# Compter les occurrences de chaque secteur
secteurs_count = secteurs_categorises.value_counts().reset_index()
secteurs_count.columns = ["Secteur", "Nombre"]

# Création du pie chart avec Plotly
fig = px.pie(secteurs_count, names="Secteur", values="Nombre", title="Proportions des secteurs dans 'S3 LINKED SECTOR (Select)'")
fig.show()
