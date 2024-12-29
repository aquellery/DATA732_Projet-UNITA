import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from geopy.geocoders import Nominatim
from lecture_excel import get_feuilles
from lecture_excel import get_donnees_colonne
import liste_contacts
import time

def transform_adress_to_coordinates(city, country):
    geolocator=Nominatim(user_agent="geoapi")
    time.sleep(1) # to avoid overloading the API
    adress=f"{city}, {country}"
    try:
        location=geolocator.geocode(adress)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error geocoding the adresse= {adress}: {e}")
        pass


def get_uni_info():
    uni_data=get_donnees_colonne("RIS", ['Institution Name', 'English Institution Name', 'Country Code', 'Name of the city', 'Region of establishment (NUTS 2)'])

    # get coordinates for each university
    uni_info=[]
    for univ in uni_data['English Institution Name']:
        name=uni_data['Institution Name'][univ]
        english_name=uni_data['English Institution Name'][univ]
        city=uni_data['Name of the city'][univ]
        country=uni_data['Country Code'][univ]
        region=uni_data['Region of establishment (NUTS 2)'][univ]
        code=uni_data['Country Code'][univ]
        coordinates=transform_adress_to_coordinates(city, country)
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

def get_companies_info():
    comanies_info=get_donnees_colonne("spinoffs contacts", ['PARTNER (SELECT)', 'NAME OF THE SPIN-OFF', 'WEBSITE', 'CONTACT PERSON', 'CONTACT MAIL', 'S3 LINKED SECTOR (Select)', 'ACTIVITY OF THE SPIN-OFF (explain)'])
    df_companies=pd.DataFrame(comanies_info)
    return df_companies


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
    "HES-SO": "Haute-école spécialisée de Suisse occidentale",
    "Université Savoie Mont Blanc": "Université de Savoie Mont Blanc"

}
data_contacts['Institution Name']=data_contacts['Institution Name'].replace(correspondance)
all_data=pd.merge(data, data_contacts, on='Institution Name', how='left')

df_companies=get_companies_info()
df_companies['PARTNER (SELECT)']=df_companies['PARTNER (SELECT)'].replace(correspondance)

app=dash.Dash(__name__)

app.layout=html.Div([
    dcc.Location(id='url', refresh=False),  #for navigation and updating the URL
    html.H1("Map of Universities by Domain", style={'text-align': 'center'}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='domain_choice',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in data_domain],
                placeholder="Select a domain",
                multi=True
            ),

            dcc.Graph(
                id='map_display'
            )
        ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top'}),  # Carte à gauche

        html.Div([
            html.Div(id='university_details', style={'margin-left': '20px'})  # Infos de l'université à droite
        ], style={'width': '28%', 'display': 'inline-block', 'vertical-align': 'top'})  # Détails à droite
    ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between'})

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
            text='Institution Name',
            color='Institution Name',
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
            text='Institution Name',
            color='Institution Name',
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
        hovermode='closest',
        showlegend=False, # we don't need to have the name of the universities since they are already on the map
    )
    return fig

# informations about the companies that are linked to the uni
@app.callback(
    Output('university_details', 'children'),
    [Input('map_display', 'clickData'), Input('domain_choice', 'value')]
)
def display_university_info(clickData, selected_domains):
    if clickData is None:
        return "Select a domain and click on a university to see the linked companies."

    # name of the uni that you cliked one
    selected_uni=clickData['points'][0]['text']
   
    # info on the selected uni
    companies_info=df_companies[df_companies['PARTNER (SELECT)']==selected_uni]

    # companies with the selected domain
    if selected_domains and 'All' not in selected_domains:
        companies_info=companies_info[companies_info['S3 LINKED SECTOR (Select)'].isin(selected_domains)]

    if companies_info.empty:
        if selected_domains and 'All' not in selected_domains:
            return f"No companies found for {selected_uni} in the selected domain(s): {', '.join(selected_domains)}."
        else:
            return f"No companies found for {selected_uni}."
    
    companies_details=[]
    # informations about the companie linked to the university and the domain
    for i, row in companies_info.iterrows():
        company_info=html.Div([
            html.H4(row['NAME OF THE SPIN-OFF']),
            html.P(f"Website: {row['WEBSITE']}" if pd.notna(row['WEBSITE']) else "Website: Unable"),
            html.P(f"Contact: {row['CONTACT PERSON']} ({row['CONTACT MAIL']})"),
            html.P(f"Activity: {row['ACTIVITY OF THE SPIN-OFF (explain)']}")
        ], style={'margin-bottom': '20px'})

        companies_details.append(company_info)

    if selected_domains and 'All' not in selected_domains: 
        return html.Div([
            html.H4(f"Companies linked to {selected_uni} for {selected_domains}: "),
            html.Div(companies_details)
        ])
    else:  
        return html.Div([
            html.H4(f"Companies linked to {selected_uni} : "),
            html.Div(companies_details)
        ])

if __name__ == "__main__":
    app.run_server(debug=True)
