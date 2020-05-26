import json
import requests

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, register_david_janzen, login_david_janzen, create_portfolio


class GetWatchlistTests(TestConfiguration):
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

        self.portfolio_id = portfolio_data['id']
        self.url = self.base_url + '/watchlists'

    def test_get_watchlist_one_item(self):
        watchlist_ticker_1_res = requests.post(url=self.url,
                                               data=json.dumps({'portfolioId': self.portfolio_id, 'ticker': 'AMD'}),
                                               headers=self.headers)
        self.assertEquals(watchlist_ticker_1_res.status_code, 200)

        res = requests.get(url=f"{self.url}/{self.portfolio_id}", headers=self.headers)
        self.assertEquals(res.status_code, 200)

        data = res.json()
        self.assertEquals(data[0]['id'], 1)
        self.assertEquals(data[0]['portfolioId'], 1)
        self.assertEquals(data[0]['ticker'], 'AMD')
        self.assertIsNotNone(data[0]['price'])

    def test_get_watchlist_multiple_items(self):
        # Adding a few watchlist items
        watchlist_ticker_1_res = requests.post(url=self.url,
                                               data=json.dumps({'portfolioId': self.portfolio_id, 'ticker': 'AMD'}),
                                               headers=self.headers)
        self.assertEquals(watchlist_ticker_1_res.status_code, 200)
        watchlist_ticker_2_res = requests.post(url=self.url,
                                               data=json.dumps({'portfolioId': self.portfolio_id, 'ticker': 'FB'}),
                                               headers=self.headers)
        self.assertEquals(watchlist_ticker_2_res.status_code, 200)
        watchlist_ticker_3_res = requests.post(url=self.url,
                                               data=json.dumps({'portfolioId': self.portfolio_id, 'ticker': 'TSLA'}),
                                               headers=self.headers)
        self.assertEquals(watchlist_ticker_3_res.status_code, 200)

        res = requests.get(url=f"{self.url}/{self.portfolio_id}", headers=self.headers)
        self.assertEquals(res.status_code, 200)

        data = res.json()
        self.assertEquals(len(data), 3)

    def test_get_watchlist_not_authorized(self):
        res = requests.get(f"{self.url}/2", headers=self.headers)
        self.assertEquals(res.status_code, 403)

    def tearDown(self):
        self.deleteTables(['League', 'User', 'Portfolio', 'Watchlist', 'PortfolioHistory'])
