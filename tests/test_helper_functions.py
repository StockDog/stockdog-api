import json
import requests


def register_david_janzen(base_url, headers):
    registerUrl = base_url + '/users'
    registerBody = {
        'firstName': 'Dave',
        'lastName': 'Janzen',
        'email': 'dave.janzen18@gmail.com',
        'password': 'Stockd2g'
    }
    registerResponse = requests.post(url=registerUrl, data=json.dumps(registerBody), headers=headers)
    return registerResponse.json()

def login_david_janzen(base_url, headers):
    loginUrl = base_url + '/users/session'
    loginBody = {
        'email': 'dave.janzen18@gmail.com',
        'password': 'Stockd2g'
    }
    loginResponse = requests.post(url=loginUrl, data=json.dumps(loginBody), headers=headers)
    return loginResponse.json()


def create_league(base_url, headers):
    # creating league
    league_base_url = base_url + '/leagues'
    post_league_body = {
        "name": 'test-league',
        "startPos": 5000,
        "start": '01-15-2020',
        "end": '02-15-2020'
    }
    league_response = requests.post(url=league_base_url,
                                    data=json.dumps(post_league_body), headers=headers)
    league_response_data = league_response.json()

    return league_response_data

def create_portfolio(base_url, headers, invite_code):
    portfolioUrl = base_url + '/portfolios'
    portfolioBody = {
        'name': 'mynewportfolio',
        'inviteCode': invite_code
    }
    portfolioResponse = requests.post(url=portfolioUrl, data=json.dumps(portfolioBody), headers=headers)
    return portfolioResponse.json()

