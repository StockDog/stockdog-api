import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import register_david_janzen, login_david_janzen, create_league, create_portfolio


class PostTransactionTests(TestConfiguration):
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

      self.user_id = login_data['userId']
      self.token = login_data['token']

      self.portfolioId = portfolio_data['id']
      self.url = self.base_url + '/transactions'


   def test_post_transaction_missingContentTypeHeader(self):
      self.headers.pop('Content-Type')
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_post_transaction_invalidContentTypeHeader(self):
      self.headers['Content-Type'] = 'plain/text'
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of ['application/json']")


   def test_post_transaction_buy(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)

   
   def test_post_transaction_sell(self):
      buyBody = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }
      buyResponse = requests.post(url=self.url, data=json.dumps(buyBody), headers=self.headers)
      buyResponseData = self.getJson(buyResponse)

      self.assertEquals(buyResponse.status_code, 200)
      self.assertTrue('id' in buyResponseData)
      self.assertTrue(buyResponseData['id'] > 0)

      sellBody = {
         "shareCount" : 2,
         "ticker" : "AMD",
         "action" : "SELL",
         "portfolioId" : self.portfolioId
      }
      sellResponse = requests.post(url=self.url, data=json.dumps(sellBody), headers=self.headers)
      sellResponseData = self.getJson(sellResponse)

      self.assertEquals(sellResponse.status_code, 200)
      self.assertTrue('id' in sellResponseData)
      self.assertTrue(sellResponseData['id'] > 0)


   def test_post_transaction_notLoggedIn(self):
      logoutUrl = self.base_url + '/users/' + str(self.user_id) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      buyBody = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }
      buyResponse = requests.post(url=self.url, data=json.dumps(buyBody), headers=self.headers)
      buyResponseData = self.getJson(buyResponse)

      self.assertEquals(buyResponse.status_code, 401)
      self.assertTrue('NotLoggedIn' in buyResponseData)
      self.assertTrue(buyResponseData['NotLoggedIn'], 'User must be logged in.')


   def test_post_transaction_notOwnedByUser(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : 16
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)

      self.assertEquals(response.status_code, 403)

   
   def test_post_transaction_missingShareCount(self):
      body = {
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'shareCount is a required field')


   def test_post_transaction_missingTicker(self):
      body = {
         "shareCount": 5,
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'ticker is a required field')

   
   def test_post_transaction_missingAction(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'action is a required field')

      
   def test_post_transaction_missingPortfolioId(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY"
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'portfolioId is a required field')


   def test_post_transaction_invalidShareCount(self):
      body = {
         "shareCount" : -3,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'shareCount must be a positive integer')
   

   def test_post_transaction_invalidTicker(self):
      body = {
         "shareCount" : 5,
         "ticker" : "FUCK",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('UnsupportedTicker' in responseData)
      self.assertEquals(responseData['UnsupportedTicker'], "The stock ticker is either invalid or unsupported.")

   
   def test_post_transaction_invalidAction(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "CALLOPTION",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'action must be a valid action: BUY, SELL')


   def test_post_transaction_invalidPortfolioId(self):
      body = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId * -1
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'portfolioId must be a positive integer')

   
   def test_post_transaction_notEnoughBuyPower(self):
      body = {
         "shareCount" : 1000000,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InsufficientBuyPower' in responseData)
      self.assertEquals(responseData['InsufficientBuyPower'], "Insufficient buy power to make purchase.")

   
   def test_post_transaction_notEnoughShareCount(self):
      buyBody = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }
      buyResponse = requests.post(url=self.url, data=json.dumps(buyBody), headers=self.headers)
      buyResponseData = self.getJson(buyResponse)

      self.assertEquals(buyResponse.status_code, 200)
      self.assertTrue('id' in buyResponseData)
      self.assertTrue(buyResponseData['id'] > 0)

      sellBody = {
         "shareCount" : 50,
         "ticker" : "AMD",
         "action" : "SELL",
         "portfolioId" : self.portfolioId
      }
      sellResponse = requests.post(url=self.url, data=json.dumps(sellBody), headers=self.headers)
      sellResponseData = self.getJson(sellResponse)

      self.assertEquals(sellResponse.status_code, 400)
      self.assertTrue('InsufficientShares' in sellResponseData)
      self.assertEquals(sellResponseData['InsufficientShares'], "Insufficient shares owned to make sale.")

   
   def test_post_transaction_noShareCount(self):
      sellBody = {
         "shareCount" : 50,
         "ticker" : "AMD",
         "action" : "SELL",
         "portfolioId" : self.portfolioId
      }
      sellResponse = requests.post(url=self.url, data=json.dumps(sellBody), headers=self.headers)
      sellResponseData = self.getJson(sellResponse)

      self.assertEquals(sellResponse.status_code, 400)
      self.assertTrue('InsufficientShares' in sellResponseData)
      self.assertEquals(sellResponseData['InsufficientShares'], "Insufficient shares owned to make sale.")



   def tearDown(self):
      self.deleteTables(['Transaction', 'Portfolio', 'User', 'League', 'PortfolioItem', 'PortfolioHistory'])
