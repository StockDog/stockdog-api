import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, register_david_janzen, login_david_janzen, create_portfolio


class GetLeagueTests(TestConfiguration):
    def setUp(self):
        self.headers = {'content-type': 'application/json'}

        register_data = register_david_janzen(self.base_url, self.headers)
        self.assertTrue('id' in register_data)
        self.assertTrue(register_data['id'] > 0)

        login_data = login_david_janzen(self.base_url, self.headers)
        self.assertIsNotNone(login_data['userId'])
        self.assertIsNotNone(login_data['token'])
        self.headers['Authorization'] = 'token ' + login_data['token']

        league_data = create_league(self.base_url, self.headers)
        self.assertIsNotNone(league_data['id'])
        self.assertIsNotNone(league_data['inviteCode'])
        self.assertIsNotNone(league_data['startPos'])

        portfolio_data = create_portfolio(self.base_url, self.headers, league_data['inviteCode'])
        self.assertTrue('id' in portfolio_data)
        self.assertTrue(portfolio_data['id'] > 0)
        self.assertTrue('buyPower' in portfolio_data)
        self.assertEquals(portfolio_data['buyPower'], 5000)

        self.portfolioId = portfolio_data['id']
        self.invite_code = league_data['inviteCode']
        self.url = self.base_url + '/portfolios'

    def test_get_league(self):
        response = requests.get(url=f"{self.base_url}/leagues/1",
                                headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(responseData["id"], 1)
        self.assertEquals(responseData["name"], "test-league")
        self.assertEquals(responseData["startPos"], 5000)
        self.assertEquals(responseData["start"], "Fri, 15 Jan 2021 00:00:00 GMT")
        self.assertEquals(responseData["end"], "Mon, 15 Feb 2021 00:00:00 GMT")
        self.assertEquals(len(responseData["portfolios"]), 1)
        self.assertEquals(responseData["portfolios"][0]["id"], 1)
        self.assertEquals(responseData["portfolios"][0]["name"], "mynewportfolio")
        self.assertEquals(type(responseData["portfolios"][0]["value"]), float)
        self.assertEquals(responseData["inviteCode"], self.invite_code)
        self.assertIsNotNone(responseData['status'])

    def test_get_league_non_existant_id(self):
        response = requests.get(url=f"{self.base_url}/leagues/2",
                                headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 404)

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User', 'League', 'PortfolioHistory'])
