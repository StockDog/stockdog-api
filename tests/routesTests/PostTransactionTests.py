import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class PostTransactionTests(TestConfiguration):
   def setUp(self):
      self.headers = {'content-type' : 'application/json'}

      registerUrl = self.baseUrl + '/users'
      registerBody = {
         'firstName' : 'Dave',
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      registerResponse = requests.post(url=registerUrl, data=json.dumps(registerBody), headers=self.headers)
      registerResponseData = self.getJson(registerResponse)
      self.assertEqual(registerResponse.status_code, 200)
      self.assertTrue('id' in registerResponseData)
      self.assertTrue(registerResponseData['id'] > 0)
      

      loginUrl = self.baseUrl + '/users/session'
      loginBody = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      loginResponse = requests.post(url=loginUrl, data=json.dumps(loginBody), headers=self.headers)
      loginResponseData = self.getJson(loginResponse)
      self.assertEqual(loginResponse.status_code, 200)
      self.assertIsNotNone(loginResponseData['userId'])
      self.assertIsNotNone(loginResponseData['token'])
      
      self.userId = loginResponseData['userId']
      self.token = loginResponseData['token']
      self.headers['Authorization'] = 'token ' + self.token

      portfolioUrl = self.baseUrl + '/portfolios'
      portfolioBody = {
         'name' : 'mynewportfolio',
      }
      portfolioResponse = requests.post(url=portfolioUrl, data=json.dumps(portfolioBody), headers=self.headers)
      portfolioResponseData = self.getJson(portfolioResponse)
      self.assertEquals(portfolioResponse.status_code, 200)
      self.assertTrue('id' in portfolioResponseData)
      self.assertTrue(portfolioResponseData['id'] > 0)
      self.assertTrue('buyPower' in portfolioResponseData)
      self.assertEquals(portfolioResponseData['buyPower'], 10000)

      self.portfolioId = portfolioResponseData['id']
      self.url = self.baseUrl + '/transactions'


   def test_post_transaction_missingContentTypeHeader(self):
      self.headers.pop('content-type')
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
      self.headers['content-type'] = 'plain/text'
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
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


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
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
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
      self.deleteTables(['Transaction', 'Portfolio', 'User'])
