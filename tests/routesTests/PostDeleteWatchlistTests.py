import json
import requests

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, register_david_janzen, login_david_janzen, create_portfolio


class PostWatchlistTests(TestConfiguration):
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

        self.portfolio_id = portfolio_data['id']
        self.url = self.base_url + '/watchlists'

    def test_post_watchlist(self):
        body = {
            'portfolioId': self.portfolio_id,
            'ticker': 'AMD'
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 200)

        response_data = response.json()
        self.assertEquals(response_data['id'], 1)

    def test_double_post_watchlist(self):
        body = {
            'portfolioId': self.portfolio_id,
            'ticker': 'AMD'
        }
        requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 400)

    def test_post_watchlist_invalid_ticker(self):
        body = {
            'portfolioId': self.portfolio_id,
            'ticker': 'FUCK'
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 400)

    def test_post_watchlist_invalid_portfolio(self):
        body = {
            'portfolioId': 2,
            'ticker': 'AMD'
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 403)

    def test_del_watchlist(self):
        body = {
            'portfolioId': self.portfolio_id,
            'ticker': 'AMD'
        }
        requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        response = requests.delete(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 200)

        response_data = response.json()
        self.assertEquals(response.status_code, 200)

    def test_del_watchlist_invalid_ticker(self):
        body = {
            'portfolioId': self.portfolio_id,
            'ticker': 'FUCK'
        }
        response = requests.delete(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 400)

    def test_del_watchlist_invalid_portfolio(self):
        body = {
            'portfolioId': 2,
            'ticker': 'AMD'
        }

        response = requests.delete(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 403)

    def test_del_watchlist_non_existant(self):
        body = {
            'portfolioId': 1,
            'ticker': 'WMT'
        }

        response = requests.delete(url=self.url, data=json.dumps(body), headers=self.headers)
        self.assertEquals(response.status_code, 400)

    def tearDown(self):
        self.deleteTables(['League', 'User', 'Portfolio', 'Watchlist'])
