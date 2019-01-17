import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class GetPortfolioTests(TestConfiguration):
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

      self.portfolioId = int(portfolioResponseData['id'])
      self.url = self.baseUrl + '/portfolios'


   def test_getPortfolio_havingNoPortfolioItems(self):
      url = self.url + '/' + str(self.portfolioId)
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('name' in responseData)
      self.assertTrue(responseData['name'], 'mynewportfolio')
      self.assertTrue('buyPower' in responseData)
      self.assertEquals(responseData['buyPower'], 10000)
      self.assertTrue('userId' in responseData)
      self.assertEquals(responseData['userId'], 1)
      self.assertTrue('leagueId' in responseData)
      self.assertEquals(responseData['leagueId'], None)
      self.assertTrue('value' in responseData)
      self.assertEquals(responseData['value'], 10000)
      self.assertTrue('items' in responseData)
      self.assertEquals(len(responseData['items']), 0)


   def test_getPortfolio_havingPortfolioItems(self):
      buyBody = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
      }
      transactionUrl = self.baseUrl + '/transactions'
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
      self.assertTrue('leagueId' in responseData)
      self.assertEquals(responseData['leagueId'], None)
      self.assertTrue('value' in responseData)
      self.assertTrue(responseData['value'] > 0)
      self.assertTrue('items' in responseData)
      self.assertEquals(len(responseData['items']), 1)
      self.assertTrue('ticker' in responseData['items'][0])
      self.assertEquals(responseData['items'][0]['ticker'], 'AMD')
      self.assertTrue('shareCount' in responseData['items'][0])
      self.assertEquals(responseData['items'][0]['shareCount'], 5)
      self.assertTrue('avgCost' in responseData['items'][0])
      self.assertTrue(responseData['items'][0]['avgCost'] > 0)


   def test_getPortfolio_notLoggedIn(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)
      
      url = self.url + '/' + str(self.portfolioId)
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")


   def test_getPortfolio_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      url = self.url + '/' + str(self.portfolioId)
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_getPortfolio_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      url = self.url + '/' + str(self.portfolioId)
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
 
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_getPortfolio_nonExistent(self):
      url = self.url + '/' + str(self.portfolioId + 10)
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

   
   def test_getPortfolio_doesNotBelongToUser(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      registerUrl = self.baseUrl + '/users'
      registerBody = {
         'firstName' : 'NotDave',
         'lastName' : 'NotJanzen',
         'email' : 'daveeee.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      registerResponse = requests.post(url=registerUrl, data=json.dumps(registerBody), headers=self.headers)
      registerResponseData = self.getJson(registerResponse)
      self.assertEqual(registerResponse.status_code, 200)
      self.assertTrue('id' in registerResponseData)
      self.assertTrue(registerResponseData['id'] > 0)
      

      loginUrl = self.baseUrl + '/users/session'
      loginBody = {
         'email' : 'daveeee.janzen18@gmail.com',
         'password' : 'Stockd2g'
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
      self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User'])