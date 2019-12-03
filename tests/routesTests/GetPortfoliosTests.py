import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, create_portfolio, login_david_janzen, register_david_janzen


class GetPortfoliosTests(TestConfiguration):
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
        self.url = self.base_url + '/portfolios'
        self.invite_code = league_data['inviteCode']
        self.user_id = login_data['userId']

        # Adding PortfolioHistory stuff manually
        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, DATE_SUB(CURDATE(), INTERVAL 2 DAY), %s)',
            (portfolio_data['id'], 2950))

        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, DATE_SUB(CURDATE(), INTERVAL 1 DAY), %s)',
            (portfolio_data['id'], 3000))

        self.cursor.execute('INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES(%s, NOW(), %s)',
            (portfolio_data['id'], 3010))

    def test_getPortfolios(self):
        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(responseData), 1)
        self.assertTrue('name' in responseData[0])
        self.assertEquals(responseData[0]['name'], 'mynewportfolio')
        self.assertTrue('buyPower' in responseData[0])
        self.assertEquals(responseData[0]['buyPower'], 5000)
        self.assertTrue('userId' in responseData[0])
        self.assertEquals(responseData[0]['userId'], 1)
        self.assertTrue('value' in responseData[0])
        self.assertEquals(responseData[0]['value'], 5000)
        self.assertEquals(responseData[0]['league']['id'], 1)
        self.assertEquals(responseData[0]['league']['name'], 'test-league')
        self.assertEquals(responseData[0]['league']['startPos'], 5000)
        self.assertTrue('start' in responseData[0]['league'])
        self.assertTrue('end' in responseData[0]['league'])

        # PortfolioHistory testing
        self.assertTrue('history' in responseData[0])
        self.assertEquals(len(responseData[0]['history']), 3)
        self.assertEquals(responseData[0]['history'][0]['datetime'], "11-29-2019")
        self.assertEquals(responseData[0]['history'][0]['value'], 2950.00)
        self.assertEquals(responseData[0]['history'][1]['datetime'], "11-30-2019")
        self.assertEquals(responseData[0]['history'][1]['value'], 3000.00)
        self.assertEquals(responseData[0]['history'][2]['datetime'], "12-01-2019")
        self.assertEquals(responseData[0]['history'][2]['value'], 3010.00)

    def test_getPortfolios_notLoggedIn(self):
        logoutUrl = self.base_url + '/users/' + str(self.user_id) + '/session'
        logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
        self.assertEqual(logoutResponse.status_code, 200)

        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 401)
        self.assertTrue('NotLoggedIn' in responseData)
        self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")


    def test_getPortfolios_havingNoPortfolios(self):
        self.deleteTables(['Portfolio'])

        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(responseData), 0)

    def test_getPortfolios_multiplePortfolios(self):
        portfolioBody = {
            'name': 'myothernewportfolio',
            'inviteCode': self.invite_code
        }

        portfolioResponse = requests.post(url=self.url, data=json.dumps(portfolioBody), headers=self.headers)
        portfolioResponseData = self.getJson(portfolioResponse)
        self.assertEquals(portfolioResponse.status_code, 200)
        self.assertTrue('id' in portfolioResponseData)
        self.assertTrue(portfolioResponseData['id'] > 0)
        self.assertTrue('buyPower' in portfolioResponseData)
        self.assertEquals(portfolioResponseData['buyPower'], 5000)

        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(responseData), 2)

    def test_getPortfolios_invalidQueryParameter(self):
        url = self.url + '?nonexistingquery=3'

        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(responseData), 1)
        self.assertTrue('name' in responseData[0])
        self.assertEquals(responseData[0]['name'], 'mynewportfolio')
        self.assertTrue('buyPower' in responseData[0])
        self.assertEquals(responseData[0]['buyPower'], 5000)

    def test_getPortfolios_withPortfolioItems(self):
        transactionsUrl = self.base_url + '/transactions'
        transactionBody = {
            "shareCount": 5,
            "ticker": "AMD",
            "action": "BUY",
            "portfolioId": self.portfolioId
        }

        transactionResponse = requests.post(url=transactionsUrl, data=json.dumps(transactionBody), headers=self.headers)
        transactionResponseData = self.getJson(transactionResponse)

        self.assertEquals(transactionResponse.status_code, 200)
        self.assertTrue('id' in transactionResponseData)
        self.assertTrue(transactionResponseData['id'] > 0)

        response = requests.get(url=self.url, headers=self.headers)
        responseData = self.getJson(response)

        self.assertTrue('name' in responseData[0])
        self.assertEquals(responseData[0]['name'], 'mynewportfolio')
        self.assertTrue('buyPower' in responseData[0])
        self.assertTrue(responseData[0]['buyPower'] > 0)
        self.assertTrue('userId' in responseData[0])
        self.assertEquals(responseData[0]['userId'], 1)
        self.assertTrue('value' in responseData[0])
        self.assertTrue(responseData[0]['value'] > 0)
        self.assertEquals(len(responseData[0]['items']), 1)
        self.assertTrue('ticker' in responseData[0]['items'][0])
        self.assertEquals(responseData[0]['items'][0]['ticker'], 'AMD')
        self.assertTrue('companyName' in responseData[0]['items'][0])
        self.assertEquals(responseData[0]['items'][0]['companyName'], 'Advanced Micro Devices, Inc.')
        self.assertTrue('gain' in responseData[0]['items'][0])
        self.assertTrue('shareCount' in responseData[0]['items'][0])
        self.assertEquals(responseData[0]['items'][0]['shareCount'], 5)
        self.assertTrue('avgCost' in responseData[0]['items'][0])
        self.assertTrue(responseData[0]['items'][0]['avgCost'] > 0)
        self.assertTrue('price' in responseData[0]['items'][0])
        self.assertTrue(responseData[0]['items'][0]['price'] > 0)

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User', 'League', 'PortfolioHistory'])
