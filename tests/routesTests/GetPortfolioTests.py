import json
import requests
from unittest import main
from datetime import datetime, timedelta

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, create_portfolio, login_david_janzen, register_david_janzen


class GetPortfolioTests(TestConfiguration):
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

        self.portfolioId = int(portfolio_data['id'])
        self.url = self.base_url + '/portfolios'
        self.userId = login_data['userId']

        # Adding PortfolioHistory stuff manually
        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, DATE_SUB(CURDATE(), INTERVAL 2 DAY), %s)',
            (portfolio_data['id'], 2950))

        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, DATE_SUB(CURDATE(), INTERVAL 1 DAY), %s)',
            (portfolio_data['id'], 3000))

        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, NOW(), %s)',
            (portfolio_data['id'], 3010))

    def test_getPortfolio_havingNoPortfolioItems(self):
        url = self.url + '/' + str(self.portfolioId)
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('name' in responseData)
        self.assertTrue(responseData['name'], 'mynewportfolio')
        self.assertTrue('buyPower' in responseData)
        self.assertEquals(responseData['buyPower'], 5000)
        self.assertTrue('userId' in responseData)
        self.assertEquals(responseData['userId'], 1)
        self.assertTrue('value' in responseData)
        self.assertEquals(responseData['value'], 5000)
        self.assertTrue('items' in responseData)
        self.assertEquals(len(responseData['items']), 0)
        self.assertEquals(responseData['league']['id'], 1)
        self.assertEquals(responseData['league']['name'], 'test-league')
        self.assertEquals(responseData['league']['startPos'], 5000)
        self.assertTrue('start' in responseData['league'])
        self.assertTrue('end' in responseData['league'])

    def test_getPortfolio_havingPortfolioItems(self):
        buyBody = {
            "shareCount": 5,
            "ticker": "AMD",
            "action": "BUY",
            "portfolioId": self.portfolioId
        }
        transactionUrl = self.base_url + '/transactions'
        buyResponse = requests.post(url=transactionUrl, data=json.dumps(buyBody), headers=self.headers)
        buyResponseData = self.getJson(buyResponse)

        url = self.url + '/' + str(self.portfolioId)
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('name' in responseData)
        self.assertTrue(responseData['name'], 'mynewportfolio')
        self.assertTrue('buyPower' in responseData)
        self.assertTrue(responseData['buyPower'], 0)
        self.assertTrue('userId' in responseData)
        self.assertEquals(responseData['userId'], 1)
        self.assertTrue('value' in responseData)
        self.assertTrue(responseData['value'] > 0)
        self.assertTrue('items' in responseData)
        self.assertEquals(len(responseData['items']), 1)
        self.assertTrue('ticker' in responseData['items'][0])
        self.assertEquals(responseData['items'][0]['ticker'], 'AMD')
        self.assertTrue('companyName' in responseData['items'][0])
        self.assertEquals(responseData['items'][0]['companyName'], 'Advanced Micro Devices, Inc.')
        self.assertTrue('shareCount' in responseData['items'][0])
        self.assertEquals(responseData['items'][0]['shareCount'], 5)
        self.assertTrue('avgCost' in responseData['items'][0])
        self.assertTrue(responseData['items'][0]['avgCost'] > 0)
        self.assertTrue('price' in responseData['items'][0])
        self.assertTrue(responseData['items'][0]['price'] > 0)
        self.assertTrue('gain' in responseData['items'][0])
        self.assertEquals(responseData['league']['id'], 1)
        self.assertEquals(responseData['league']['name'], 'test-league')
        self.assertEquals(responseData['league']['startPos'], 5000)
        self.assertTrue('start' in responseData['league'])
        self.assertTrue('end' in responseData['league'])

        # PortfolioHistory testing
        self.assertTrue('history' in responseData)
        self.assertEquals(len(responseData['history']), 3)
        self.assertEquals(responseData['history'][0]['datetime'], datetime.date(datetime.now() - timedelta(2)).strftime('%m-%d-%Y'))
        self.assertEquals(responseData['history'][0]['value'], 2950.00)
        self.assertEquals(responseData['history'][1]['datetime'], datetime.date(datetime.now() - timedelta(1)).strftime('%m-%d-%Y'))
        self.assertEquals(responseData['history'][1]['value'], 3000.00)
        self.assertEquals(responseData['history'][2]['datetime'], datetime.date(datetime.now()).strftime('%m-%d-%Y'))
        self.assertEquals(responseData['history'][2]['value'], 3010.00)

    def test_getPortfolio_notLoggedIn(self):
        logoutUrl = self.base_url + '/users/' + str(self.userId) + '/session'
        logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
        self.assertEqual(logoutResponse.status_code, 200)

        url = self.url + '/' + str(self.portfolioId)
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 401)
        self.assertTrue('NotLoggedIn' in responseData)
        self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")

    def test_getPortfolio_nonExistent(self):
        url = self.url + '/' + str(self.portfolioId + 10)
        response = requests.get(url=url, headers=self.headers)
        responseData = self.getJson(response)

    def test_getPortfolio_doesNotBelongToUser(self):
        logoutUrl = self.base_url + '/users/' + str(self.userId) + '/session'
        logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
        self.assertEqual(logoutResponse.status_code, 200)

        registerUrl = self.base_url + '/users'
        registerBody = {
            'firstName': 'NotDave',
            'lastName': 'NotJanzen',
            'email': 'daveeee.janzen18@gmail.com',
            'password': 'Stockd2g'
        }
        registerResponse = requests.post(url=registerUrl, data=json.dumps(registerBody), headers=self.headers)
        registerResponseData = self.getJson(registerResponse)
        self.assertEqual(registerResponse.status_code, 200)
        self.assertTrue('id' in registerResponseData)
        self.assertTrue(registerResponseData['id'] > 0)

        loginUrl = self.base_url + '/users/session'
        loginBody = {
            'email': 'daveeee.janzen18@gmail.com',
            'password': 'Stockd2g'
        }
        loginResponse = requests.post(url=loginUrl, data=json.dumps(loginBody), headers=self.headers)
        loginResponseData = self.getJson(loginResponse)
        self.assertEqual(loginResponse.status_code, 200)
        self.assertIsNotNone(loginResponseData['userId'])
        self.assertIsNotNone(loginResponseData['token'])

        token = loginResponseData['token']
        self.headers['Authorization'] = 'token ' + token

        url = self.url + '/' + str(self.portfolioId)
        response = requests.get(url=url, headers=self.headers)

        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User', 'League', 'PortfolioHistory'])
