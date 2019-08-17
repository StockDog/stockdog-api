import json
import requests


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
