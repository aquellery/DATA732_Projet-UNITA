import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from lecture_excel import get_feuilles
from lecture_excel import get_donnees_colonne
import liste_contacts
import time

def transformer_adresse_coordonnees(ville, pays, code_postal):
    geolocator=Nominatim(user_agent="geoapi")
    time.sleep(1) # pour pas surcharger l'API
    adresse=f"{code_postal}, {ville}, {pays}"
    try:
        location=geolocator.geocode(adresse)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Erreur lors de la géocodification de l'adresse {adresse}: {e}")
        pass


def get_infos_univ():
    data_univ=get_donnees_colonne("RIS", ['Institution Name', 'English Institution Name', 'Country Code', 'Name of the city','Postcode', 'Region of establishment (NUTS 2)'])

    # on récupère les coordonnées de chaque universités
    infos_univ=[]
    for univ in data_univ['English Institution Name']:
        nom=data_univ['Institution Name'][univ]
        nom_english=data_univ['English Institution Name'][univ]
        ville=data_univ['Name of the city'][univ]
        pays=data_univ['Country Code'][univ]
        code_postal=data_univ['Postcode'][univ]
        region=data_univ['Region of establishment (NUTS 2)'][univ]
        code=data_univ['Country Code'][univ]
        coordonnees=transformer_adresse_coordonnees(ville, pays, code_postal)
        infos_univ.append({'Institution Name':nom, 'English Name':nom_english, 'Country Code':code, 'Region':region, 'Coordonnees':coordonnees})

    df_infos=pd.DataFrame(infos_univ)
    print(df_infos)
    # on met des coordonnées à 0,0 pour celles en None
    df_infos['Coordonnees']=df_infos['Coordonnees'].apply(lambda x: x if x is not None else [0, 0])
    df_infos['latitude']=df_infos['Coordonnees'].apply(lambda x:x[0])
    df_infos['longitude']=df_infos['Coordonnees'].apply(lambda x:x[1])

    #pour centrer la carte
    centre_lat=df_infos['latitude'].mean()
    centre_lon=df_infos['longitude'].mean()

    return df_infos, centre_lat, centre_lon


# associer les régions des universités aux domaines
def region_univ_domaine():
    match=get_feuilles("S3 Match")
    df_match=pd.DataFrame(match)
    df_match=df_match.drop(index=[0, 1, 2])
    df_match.iloc[:, 0]=df_match.iloc[:, 0].ffill() # pour gerer la fusion des colonnes, si case vide on remet le nom qui était au dessus

    regions=df_match.iloc[0:1] # on garde la 1e ligne pour avoir les régions
    regions=regions.drop(regions.columns[0], axis=1) #on enlève la 1e colonne qui correspond aux domaines
    for region in regions.columns :
        #print(region)
        #print(regions[region].iloc[0])
        regions[region]=regions[region].iloc[0].split(' ')[0]

    liste_regions=[regions[col].iloc[0] for col in regions.columns]
    #print("liste région : ", liste_regions)
    domaines=df_match.iloc[1:, 0]
    #print('domaines', domaines)

    region_domaine_dict={region: [] for region in liste_regions}
    # parcourt des données
    for i, region in enumerate(liste_regions):
        for j, domaine in enumerate(domaines):
            if j<18 : #limite du tableau 
                cellule=df_match.iloc[j+1, i+1]
                # on regarded si la cellule est remplie
                if pd.notna(cellule) and str(cellule)!='':
                    #print(i, region, j, domaine, cellule)
                    region_domaine_dict[region].append(domaine)

    # nettoyage des domaines en double
    for region, domaines in region_domaine_dict.items():
        region_domaine_dict[region]=list(set(domaines)) #on supprime les doublons 

    return region_domaine_dict

def associer_region_univ(df_infos, regions_domaine_dict):
    df_infos["Domaines"]=df_infos["Region"].map(regions_domaine_dict)
    return df_infos

def filtrer_univ_domaine(domaine_selectionnes, data):
    #print("Data sans filtre")
    #print(data[['English Name', 'Domaine']])
    #print("Filtre en fonction du domaine ", domaine_selectionnes)
    if domaine_selectionnes:
        if 'All' in domaine_selectionnes:
            return data
        else :
            filtre=data[data['Domaine'].isin(domaine_selectionnes)]
    else :
        filtre=data
    #print("Data filtrée")
    #print(filtre[['English Name', 'Domaine']])
    return filtre

df_infos, centre_lat, centre_lon=get_infos_univ()
regions_domaine_dict=region_univ_domaine()
df_infos=associer_region_univ(df_infos, regions_domaine_dict)
#print("associations infos")
#print(df_info)
data_domaine=sorted({domaine for domaines in df_infos['Domaines'] if isinstance(domaines, list) for domaine in domaines})

# modification du data frame pour faciliter le filtrage par domaines
data=df_infos.explode('Domaines')
data.rename(columns={"Domaines": "Domaine"}, inplace=True) 

# ajout des données de contact
contacts=liste_contacts.combine_dico()
info_contact=[]
for service_type, partners in contacts.items():
    for partner, details in partners.items():
        office, contact_person, contact_mail, other_details = details
        info_contact.append({
            'Institution Name': partner,
            'Service Type': service_type,
            'Office/Service Name': office,
            'Contact Person': contact_person,
            'Contact Mail': contact_mail,
            'Other Contact Details': other_details
        })
data_contacts=pd.DataFrame(info_contact)
# gestion des différences de noms
correspondance={
    "HES-SO": "Haute-école spécialisée de Suisse occidentale"
}
data_contacts['Institution Name']=data_contacts['Institution Name'].replace(correspondance)
print("data contacts ", data_contacts)
all_data=pd.merge(data, data_contacts, on='Institution Name', how='left')
print("all data", all_data[['Institution Name', 'Domaine', 'Contact Person', 'Contact Mail']])

app=dash.Dash(__name__)

app.layout=html.Div([
    html.H1("Carte des universités et des entreprises en fonction des domaines", style={'text-align': 'center'}),

    dcc.Dropdown(
        id='choix_domaine',
        options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in data_domaine],
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
    data_filtree=filtrer_univ_domaine(domaine_selectionnes, all_data)
    pays=data_filtree['Country Code'].unique()

    if 'latitude' not in data_filtree.columns or 'longitude' not in data_filtree.columns:
        print("Erreur: les colonnes 'latitude' ou 'longitude' manquent dans le DataFrame.")
        return {}
    

    # on affiche les universités en fonction du domaine selectionné
    if not domaine_selectionnes or 'All' in domaine_selectionnes:  #si on affiche tous les domaines
            fig=px.scatter_mapbox(
            data_filtree,
            lat='latitude',
            lon='longitude',
            text='English Name',
            color='English Name',
            zoom=3,
            title="Universités en foncion des domaines",
            hover_data={
                "English Name": True,
                "latitude": False,  # Cache cette donnée de la boîte d'infos
                "longitude": False  # Cache cette donnée également
            }
        )
    else:
        fig=px.scatter_mapbox(
            data_filtree,
            lat='latitude',
            lon='longitude',
            text='English Name',
            color='English Name',
            zoom=3,
            title="Universités en foncion des domaines",
            hover_data={
                "English Name": True,
                "Domaine": True,
                "Contact Person": True,
                "Contact Mail": True,
                "Other Contact Details": True,
                "latitude": False,  # Cache cette donnée de la boîte d'infos
                "longitude": False  # Cache cette donnée également
            }
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
