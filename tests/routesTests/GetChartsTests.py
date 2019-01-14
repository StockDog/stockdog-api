import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class GetChartsTests(TestConfiguration):

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
      self.url = self.baseUrl + '/charts'


   def test_getCharts_recent(self):
      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertEquals(len(responseData), 1)
   

   def test_getCharts_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_getCharts_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_getCharts_notLoggedIn(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
   
   
   def test_getCharts_wrongAuthHeader(self):
      self.headers['Authorization'] = 'notToken ' + self.token

      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
      

   def test_getCharts_missingToken(self):
      self.headers['Authorization'] = 'token '

      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
   

   def test_getCharts_wrongToken(self):
      self.headers['Authorization'] = 'Token ' + 'some1131nonsensetoken'

      url = self.url + '/AMD?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")


   def test_getCharts_day(self):
      url = self.url + '/MSFT?length=day'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
   

   def test_getCharts_week(self):
      url = self.url + '/TSLA?length=week'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
      

   def test_getCharts_month(self):
      url = self.url + '/AAPL?length=month'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
   

   def test_getCharts_year(self):
      url = self.url + '/AMZN?length=year'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
      

   def test_getCharts_noTicker(self):
      url = self.url + '?length=year'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 404)


   def test_getCharts_noLength(self):
      url = self.url + '/SNAP'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'length is a required field')
      
      
   def test_getCharts_noLengthAndTicker(self):
      url = self.url + '?'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 404)


   def test_getCharts_invalidLength(self):
      url = self.url + '/SNAP?length=forever'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "length is not one of 'day', 'week', 'month', 'year', or 'recent'")


   def test_getCharts_invalidTicker(self):
      url = self.url + '/YOLO?length=day'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidTicker' in responseData)
      self.assertEquals(responseData['InvalidTicker'], "The stock ticker is either invalid or unsupported.")


   def tearDown(self):
      self.deleteTables(['User'])


if __name__ == "__main__":
   main()