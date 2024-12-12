import pandas as pd

file_name = '../data/data_entreprises.xlsx'  # File name
print(file_name)

df = pd.read_excel(file_name) 
# Affichage des premières lignes du DataFrame 
print(df.head())