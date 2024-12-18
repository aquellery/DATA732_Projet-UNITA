from lecture_excel import get_contact_company_internship, get_contact_tech_transfer, get_contact_incubator
import pandas as pd
import plotly.express as px

dico_tech = get_contact_tech_transfer(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])
dico_company = get_contact_company_internship(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])
dico_incubator = get_contact_incubator(['PARTNER','OFFICE/SERVICE NAME','CONTACT PERSON','CONTACT MAIL','OTHER CONTACT DETAILS'])

print(dico_incubator)

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

        transformed[partner] = [office, contact_person, contact_mail, other_details]
    
    return transformed

transformed_tech = transform_dictionary(dico_tech)
transformed_company = transform_dictionary(dico_company)
transformed_incubator = transform_dictionary(dico_incubator)
print(transformed_tech)
