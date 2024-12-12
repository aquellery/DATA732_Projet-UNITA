import math
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from lecture_excel import get_feuilles
from lecture_excel import get_donnees_colonne


def transformer_adresse_coordonnees(ville, pays, code_postal):
    geolocator=Nominatim(user_agent="geoapi")
    adresse=f"{code_postal}, {ville}, {pays}"
    try:
        location = geolocator.geocode(adresse)
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"Erreur lors de la géocodification de l'adresse {adresse}")
            pass
    except Exception as e:
        print(f"Erreur lors de la géocodification de l'adresse {adresse}: {e}")
        pass

def trier_univ_domaine(domaine, liste_univ):
    pass

data_univ=get_donnees_colonne("RIS", ['English Institution Name', 'Country Code', 'Name of the city','Postcode'])

# on récupère les coordonnées de chaque universités
coordonnees_univ=[]
for univ in data_univ['English Institution Name']:
    nom=data_univ['English Institution Name'][univ]
    ville=data_univ['Name of the city'][univ]
    pays=data_univ['Country Code'][univ]
    code_postal=data_univ['Postcode'][univ]
    coordonnees=transformer_adresse_coordonnees(ville, pays, code_postal)
    coordonnees_univ.append({'Institution Name':nom, 'Coordonnees':coordonnees})

df_coordonnees=pd.DataFrame(coordonnees_univ)
print(df_coordonnees)
# on met des coordonnées à 0,0 pour celles en None
df_coordonnees['Coordonnees']=df_coordonnees['Coordonnees'].apply(lambda x: x if x is not None else [0, 0])
df_coordonnees['latitude']=df_coordonnees['Coordonnees'].apply(lambda x:x[0])
df_coordonnees['longitude']=df_coordonnees['Coordonnees'].apply(lambda x:x[1])

#pour centrer la carte
centre_lat=df_coordonnees['latitude'].mean()
centre_lon=df_coordonnees['longitude'].mean()

# on récupère les différents domaines
data_domaine=get_donnees_colonne("S3 Match", ["GENERAL THEMATIC"])
data_domaine={ #nettoyage des données
    'GENERAL THEMATIC': 
    { key: value for key, value in data_domaine['GENERAL THEMATIC'].items()
     if not (isinstance(value, float) and math.isnan(value))}
}

"""
TODO : feuille S3 Match pour lier les univs aux domaines
"""


app=dash.Dash(__name__)

app.layout=html.Div([
    html.H1("Carte des universités et des entreprises en fonction des domaines", style={'text-align': 'center'}),

    dcc.Dropdown(
        id='choix_domaine',
        options=[{'label': i, 'value': i} for i in data_domaine],
        placeholder="Sélectionnez un domaine",
        multi=True
    ),

    dcc.Graph(
        id='affichage_carte'
    )
])

#Callback en fonction du domaine
@app.callback(
    Output('affichage_carte', 'figure'),
    [Input('choix_domaine', 'value')]
)

def update_map(domaine_selectionnes):
    """ TODO quand on aura le lien univ/domaine
    if domaine_selectionnes:
        data=df_data[df_data['Domaine'].isin(domaine_selectionnes)]
    else:
        data=df_data
    """

    fig=px.scatter_mapbox(
        df_coordonnees,
        lat='latitude',
        lon='longitude',
        text='Institution Name',
        color='Institution Name', # TODO : couleur en fonction des domaines plus tard
        zoom=3,
        title="Universités en foncion des domaines"
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={'lat':centre_lat, 'lon':centre_lon},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        dragmode="zoom",
        hovermode='closest'
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
