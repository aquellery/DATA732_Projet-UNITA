from lecture_excel import get_contact_company_internship, get_contact_tech_transfer, get_contact_incubator
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dico_tech = get_contact_tech_transfer(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])
dico_company = get_contact_company_internship(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])
dico_incubator = get_contact_incubator(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])

#print(dico_incubator)

def transform_dictionary(data):
    """
    Transforme un dictionnaire initial en un format souhaité.

    Paramètres :
    data (dict) : Le dictionnaire à transformer.

    Retourne :
    dict : Le dictionnaire transformé.
    """
    transformed = {}
    
    for index in data['PARTNER']:
        partner = data['PARTNER'][index]
        office = data['OFFICE/SERVICE NAME'].get(index, None)
        contact_person = data['CONTACT PERSON'].get(index, None)
        contact_mail = data['CONTACT MAIL'].get(index, None)
        other_details = data['OTHER CONTACT DETAILS'].get(index, None)

        # convert NaN to 'Unavailable'
        office="Unavailable" if pd.isna(office) else office
        contact_person="Unavailable" if pd.isna(contact_person) else contact_person
        contact_mail="Unavailable" if pd.isna(contact_mail) else contact_mail
        other_details="Unavailable" if pd.isna(other_details) else other_details

        transformed[partner] = [office, contact_person, contact_mail, other_details]
    
    return transformed

transformed_tech = transform_dictionary(dico_tech)
transformed_company = transform_dictionary(dico_company)
transformed_incubator = transform_dictionary(dico_incubator)

def combine_dico(): 
    final_dico = {}
    final_dico['TECH TRANSFER OFFICES'] = transformed_tech
    final_dico['COMPANY INTERNSHIP PROGRAMMES'] = transformed_company
    final_dico['INCUBATOR/ACCELERATOR'] = transformed_incubator
    return final_dico

#print(combine_dico())

def afficher_liste_contacts():
    dico=combine_dico()

        # Préparer les données pour le tableau
    categories = []
    institutions = []
    personnes = []
    emails = []
    telephones = []
    
    for category, insts in dico.items():
        for institution, details in insts.items():
            categories.append(category)
            institutions.append(institution)
            personnes.append(details[1])
            emails.append(details[2])
            telephones.append(details[3])
    
    # Créer le tableau
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Catégorie', 'Institution', 'Personne', 'Email', 'Téléphone'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[categories, institutions, personnes, emails, telephones],
                   fill_color='lavender',
                   align='left'))
    ])
    
    # Ajouter des titres
    fig.update_layout(
        title='Liste des personnes par catégorie'
    )

    return fig