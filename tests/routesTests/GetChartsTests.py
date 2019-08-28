import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration
from tests.test_helper_functions import register_david_janzen, login_david_janzen

class GetChartsTests(TestConfiguration):

   def setUp(self):
      self.headers = {'content-type': 'application/json'}

      register_data = register_david_janzen(self.base_url, self.headers)
      self.assertTrue('id' in register_data)
      self.assertTrue(register_data['id'] > 0)

      login_data = login_david_janzen(self.base_url, self.headers)
      self.assertIsNotNone(login_data['userId'])
      self.assertIsNotNone(login_data['token'])

      self.user_id = login_data['userId']
      self.token = login_data['token']
      self.headers['Authorization'] = 'token ' + self.token
      self.url = self.base_url + '/stocks'

   def test_getCharts_recent(self):
      url = self.url + '/AMD/chart?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertEquals(len(responseData), 1)
   

   def test_getCharts_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      url = self.url + '/AMD/chart?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_getCharts_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      url = self.url + '/AMD/chart?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_getCharts_notLoggedIn(self):
      logoutUrl = self.base_url + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      url = self.url + '/AMD/chart?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
   
   
   def test_getCharts_wrongAuthHeader(self):
      self.headers['Authorization'] = 'notToken ' + self.token

      url = self.url + '/AMD/chart?length=recent/chart'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
      

   def test_getCharts_missingToken(self):
      self.headers['Authorization'] = 'token '

      url = self.url + '/AMD/chart?length=recent/chart'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")
   

   def test_getCharts_wrongToken(self):
      self.headers['Authorization'] = 'Token ' + 'some1131nonsensetoken'

      url = self.url + '/AMD/chart?length=recent'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertEquals(responseData['NotLoggedIn'], "User must be logged in.")


   def test_getCharts_day(self):
      url = self.url + '/MSFT/chart?length=day'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
   

   def test_getCharts_week(self):
      url = self.url + '/TSLA/chart?length=week'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
      

   def test_getCharts_month(self):
      url = self.url + '/AAPL/chart?length=month'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
   

   def test_getCharts_year(self):
      url = self.url + '/AMZN/chart?length=year'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue(len(responseData) > 1)
      

   def test_getCharts_noTicker(self):
      url = self.url + '//chart?length=year'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 404)


   def test_getCharts_noLength(self):
      url = self.url + '/SNAP/chart'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'length is a required field')
      
      
   def test_getCharts_noLengthAndTicker(self):
      url = self.url + '?/chart'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 404)


   def test_getCharts_invalidLength(self):
      url = self.url + '/SNAP/chart?length=forever'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "length is not one of 'day', 'week', 'month', 'year', or 'recent'")


   def test_getCharts_invalidTicker(self):
      url = self.url + '/FUCK/chart?length=day'
      response = requests.get(url=url, headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('UnsupportedTicker' in responseData)
      self.assertEquals(responseData['UnsupportedTicker'], "The stock ticker is either invalid or unsupported.")


   def tearDown(self):
      self.deleteTables(['User'])


if __name__ == "__main__":
   main()
