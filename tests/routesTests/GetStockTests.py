import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import register_david_janzen, login_david_janzen, create_league, create_portfolio


class StockTests(TestConfiguration):
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'App-Version': '*'
        }

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
        self.userId = login_data['userId']
        self.url = self.base_url + '/stocks/'

    def test_getStock_good(self):
        url = self.url + 'amd'
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)
        self.assertEqual(responseData['companyName'], "Advanced Micro Devices, Inc.");
        self.assertTrue('currentPrice' in responseData)

    def test_getStock_nonExistent(self):
        url = self.url + 'FUCK'
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)
        self.assertEqual(responseData['UnsupportedTicker'], "The stock ticker is either invalid or unsupported.");

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User', 'League', 'PortfolioHistory'])
