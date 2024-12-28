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

def transform_adress_to_coordinates(city, country, postal_code):
    geolocator=Nominatim(user_agent="geoapi")
    time.sleep(1) # to avoid overloading the API
    adress=f"{postal_code}, {city}, {country}"
    try:
        location=geolocator.geocode(adress)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error geocoding the adresse= {adress}: {e}")
        pass


def get_uni_info():
    uni_data=get_donnees_colonne("RIS", ['Institution Name', 'English Institution Name', 'Country Code', 'Name of the city','Postcode', 'Region of establishment (NUTS 2)'])

    # get coordinates for each university
    uni_info=[]
    for univ in uni_data['English Institution Name']:
        name=uni_data['Institution Name'][univ]
        english_name=uni_data['English Institution Name'][univ]
        city=uni_data['Name of the city'][univ]
        country=uni_data['Country Code'][univ]
        postal_code=uni_data['Postcode'][univ]
        region=uni_data['Region of establishment (NUTS 2)'][univ]
        code=uni_data['Country Code'][univ]
        coordinates=transform_adress_to_coordinates(city, country, postal_code)
        uni_info.append({'Institution Name':name, 'English Name':english_name, 'Country Code':code, 'Region':region, 'Coordonnees':coordinates})

    df_infos=pd.DataFrame(uni_info)

    # set coordinates to 0,0 for thoses that are None
    df_infos['Coordonnees']=df_infos['Coordonnees'].apply(lambda x: x if x is not None else [0, 0])
    df_infos['latitude']=df_infos['Coordonnees'].apply(lambda x:x[0])
    df_infos['longitude']=df_infos['Coordonnees'].apply(lambda x:x[1])

    # map centering
    centre_lat=df_infos['latitude'].mean()
    centre_lon=df_infos['longitude'].mean()

    return df_infos, centre_lat, centre_lon


# associate university regions with domains 
def uni_region_domain():
    match=get_feuilles("S3 Match")
    df_match=pd.DataFrame(match)
    df_match=df_match.drop(index=[0, 1, 2])
    df_match.iloc[:, 0]=df_match.iloc[:, 0].ffill() # to handle column merging, if a cell is empty, we fill it with the value above

    regions=df_match.iloc[0:1] # we keep the first row to get the regions
    regions=regions.drop(regions.columns[0], axis=1) # we remove the first column that corresponds to the domains
    for region in regions.columns :
        regions[region]=regions[region].iloc[0].split(' ')[0]

    region_list=[regions[col].iloc[0] for col in regions.columns]
    domains=df_match.iloc[1:, 0]

    region_domain_dict={region: [] for region in region_list}
    # loop through the data
    for i, region in enumerate(region_list):
        for j, domain in enumerate(domains):
            if j<18 : #limit of the table
                cellule=df_match.iloc[j+1, i+1]
                # if the cell is empty
                if pd.notna(cellule) and str(cellule)!='':
                    region_domain_dict[region].append(domain)

    # clean up duplicate domains
    for region, domains in region_domain_dict.items():
        region_domain_dict[region]=list(set(domains)) #remove duplicates

    return region_domain_dict

def associate_region_to_uni(df_infos, regions_domain_dict):
    df_infos["Domains"]=df_infos["Region"].map(regions_domain_dict)
    return df_infos

def filter_uni_by_domain(selected_domains, data):
    if selected_domains:
        if 'All' in selected_domains:
            return data
        else :
            filtered=data[data['Domain'].isin(selected_domains)]
    else :
        filtered=data
    return filtered

df_infos, centre_lat, centre_lon=get_uni_info()
regions_domain_dict=uni_region_domain()
df_infos=associate_region_to_uni(df_infos, regions_domain_dict)
data_domain=sorted({domain for domains in df_infos['Domains'] if isinstance(domains, list) for domain in domains})

# modify the dataframe to simplify filtering by domains
data=df_infos.explode('Domains')
data.rename(columns={"Domains": "Domain"}, inplace=True) 

# add contact data
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

# handle name mismatches
correspondance={
    "HES-SO": "Haute-école spécialisée de Suisse occidentale"
}
data_contacts['Institution Name']=data_contacts['Institution Name'].replace(correspondance)
all_data=pd.merge(data, data_contacts, on='Institution Name', how='left')

app=dash.Dash(__name__)

app.layout=html.Div([
    html.H1("Map of Universities and Companies by Domain", style={'text-align': 'center'}),

    dcc.Dropdown(
        id='domain_choice',
        options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in data_domain],
        placeholder="Select a domain",
        multi=True
    ),

    dcc.Graph(
        id='map_display'
    )
])

#Callback based on the selected domain
@app.callback(
    Output('map_display', 'figure'),
    [Input('domain_choice', 'value')]
)

def update_map(selected_domains):
    filtered_data=filter_uni_by_domain(selected_domains, all_data)

    if 'latitude' not in filtered_data.columns or 'longitude' not in filtered_data.columns:
        print("Error: 'latitude' or 'longitude' columns are missing ")
        return {}
    

    # display uni based on selected domain
    if not selected_domains or 'All' in selected_domains:  #if displaying all domains
        fig = px.scatter_mapbox(
            filtered_data,
            lat='latitude',
            lon='longitude',
            text='English Name',
            color='English Name',
            zoom=3,
            title="Universities by Domains",
            hover_data={
                "English Name": True,
                "latitude": False, # we don't want this data in the info box
                "longitude": False # we don't want this data in the info box
            }
        )
    else:
        fig=px.scatter_mapbox(
            filtered_data,
            lat='latitude',
            lon='longitude',
            text='English Name',
            color='English Name',
            zoom=3,
            title="Universities by Domains",
            hover_data={
                "English Name": True,
                "Domain": True,
                "Contact Person": True,
                "Contact Mail": True,
                "Other Contact Details": True,
                "latitude": False, # we don't want this data in the info box
                "longitude": False # we don't want this data in the info box
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
