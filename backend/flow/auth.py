import requests as r
from os import environ
from time import time
from typing import Optional

auth_data = {
    'client_id': environ['AUTH0_CLIENT'],
    'username': environ['AUTH0_USER'],
    'password': environ['AUTH0_PWD'],
    'grant_type': 'password',
    'scope': 'openid email'
}

auth_url = "https://akvofoundation.eu.auth0.com/oauth/token"
flow_api_url = "https://api-auth0.akvo.org/flow/orgs/seap"
tc_api_url = "http://tech-consultancy.akvo.org/akvo-flow-web-api/seap"
form_definition_url = f"{tc_api_url}/#form#/update"
data_url = f"{flow_api_url}/form_instances?survey_id=#survey#&form_id=#form#"
init_sync_url = f"{flow_api_url}/sync?initial=true"

# Farmer test survey from Demo Survey
survey_id = 6087710401888256
registraton_form = 6286483501613056
monitoring_form = 5968064826834944


def get_token():
    account = r.post(auth_url, auth_data)
    try:
        account = account.json()
    except ValueError:
        print('FAILED: TOKEN ACCESS UNKNOWN')
        return False
    return {'token': account['id_token'], 'time': time()}


def get_header(token: dict):
    return {
        'Authorization': f"Bearer {token['token']}",
        'Accept': 'application/vnd.akvo.flow.v2+json',
        'Content-Type': 'application/json'
    }


def get_data(url: str, token: dict):
    header = get_header(token)
    response = r.get(url, headers=header)
    print("FETCH: " + str(response.status_code) + " | " + url)
    if response.status_code == 200:
        response = response.json()
        return response
    print("ERROR: " + url)
    return None


def get_form(token: dict, form_id: int):
    url = form_definition_url.replace('#form#', str(form_id))
    return get_data(url=url, token=token)


def get_datapoint(
    token: dict,
    survey_id: int,
    form_id: int,
    page_size: Optional[int] = None,
):
    url = data_url.replace("#survey#", str(survey_id))
    url = url.replace("#form#", str(form_id))
    if (page_size):
        url = f"{url}&page_size={page_size}"
    return get_data(url=url, token=token)


def init_sync(token: dict):
    return get_data(url=init_sync_url, token=token)
