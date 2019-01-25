import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class GetPortfoliosTests(TestConfiguration):
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
      self.url = self.baseUrl + '/portfolios'
      

   def test_getPortfolios(self):
      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertEquals(len(responseData), 1)
      self.assertTrue('name' in responseData[0])
      self.assertEquals(responseData[0]['name'], 'mynewportfolio')
      self.assertTrue('buyPower' in responseData[0])
      self.assertEquals(responseData[0]['buyPower'], 10000)
      self.assertTrue('userId' in responseData[0])
      self.assertEquals(responseData[0]['userId'], 1)
      self.assertTrue('leagueId' in responseData[0])
      self.assertEquals(responseData[0]['leagueId'], None)
      self.assertTrue('value' in responseData[0])
      self.assertEquals(responseData[0]['value'], 10000)


   def test_getPortfolios_notLoggedIn(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")


   def test_getCharts_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_getCharts_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")
   

   def test_getPortfolios_havingNoPortfolios(self):
      self.deleteTables(['Portfolio'])

      response = requests.get(url=self.url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertEquals(len(responseData), 0)
      

   def test_getPortfolios_multiplePortfolios(self):
      portfolioBody = {
         'name' : 'myothernewportfolio'
      }
      
      portfolioResponse = requests.post(url=self.url, data=json.dumps(portfolioBody), headers=self.headers)
      portfolioResponseData = self.getJson(portfolioResponse)
      self.assertEquals(portfolioResponse.status_code, 200)
      self.assertTrue('id' in portfolioResponseData)
      self.assertTrue(portfolioResponseData['id'] > 0)
      self.assertTrue('buyPower' in portfolioResponseData)
      self.assertEquals(portfolioResponseData['buyPower'], 10000)

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
      self.assertEquals(responseData[0]['buyPower'], 10000)


   def test_getPortfolios_withPortfolioItems(self):
      transactionsUrl = self.baseUrl + '/transactions'
      transactionBody = {
         "shareCount" : 5,
         "ticker" : "AMD",
         "action" : "BUY",
         "portfolioId" : self.portfolioId
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
      self.assertTrue('leagueId' in responseData[0])
      self.assertEquals(responseData[0]['leagueId'], None)
      self.assertTrue('value' in responseData[0])
      self.assertTrue(responseData[0]['value'] > 0)
      self.assertEquals(len(responseData[0]['items']), 1)
      self.assertTrue('ticker' in responseData[0]['items'][0])
      self.assertEquals(responseData[0]['items'][0]['ticker'], 'AMD')
      self.assertTrue('shareCount' in responseData[0]['items'][0])
      self.assertEquals(responseData[0]['items'][0]['shareCount'], 5)
      self.assertTrue('avgCost' in responseData[0]['items'][0])
      self.assertTrue(responseData[0]['items'][0]['avgCost'] > 0)


   def tearDown(self):
      self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User'])