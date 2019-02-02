import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class PostLeagueTests(TestConfiguration):
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

      self.url = self.baseUrl + '/leagues'


   def test_post_league_missingContentTypeHeade(self):
      self.headers.pop('content-type')
      body = {
         "name": "myLeague",
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_post_league_invalidContentTypeHeade(self):
      self.headers['content-type'] = 'plain/text'
      body = {
         "name": "myLeague",
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_post_league_notLoggedIn(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
      self.assertEqual(logoutResponse.status_code, 200)

      body = {
         "name": "myLeague",
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }      
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertTrue(responseData['NotLoggedIn'], 'User must be logged in.')


   def test_post_league_missingName(self):
      body = {
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000         
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'name is a required field')

   
   def test_post_league_missingStart(self):
      body = {
         "name": "myLeague",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'start is a required field')


   def test_post_league_missingEnd(self):
      body = {
         "name": "myLeague",
         "start": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'end is a required field')

   
   def test_post_league_invalidName(self):
      body = {
         "name": 23113,
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'name is not a string or formatted incorrectly')
   

   def test_post_league_emptyName(self):
      body = {
         "name": '',
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'name must not be empty')


   def test_post_league_invalidStart(self):
      body = {
         "name": 'myLeague',
         "start": "08/24/2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'start must be in MM-DD-YYYY format')


   def test_post_league_invalidEnd(self):
      body = {
         "name": 'myLeague',
         "start": "08-24-2019",
         "end": "08/30/2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'end must be in MM-DD-YYYY format')


   def test_post_league_negativeStartPos(self):
      body = {
         "name": 'myLeague',
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": -3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'startPos must be a value between 0 and 10000000')

     
   def test_post_league_highStartPos(self):
      body = {
         "name": 'myLeague',
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 300000000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'startPos must be a value between 0 and 10000000')


   def test_post_league_pastStartDate(self):
      body = {
         "name": 'myLeague',
         "start": "08-24-2017",
         "end": "04-30-2018",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "start date of the league can't be in the past")
       

   def test_post_league_pastEndDate(self):
      body = {
         "name": 'myLeague',
         "start": "08-24-2018",
         "end": "04-30-2017",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "end date of the league can't be in the past")
       
   def test_post_league_endBeforeStart(self):
      body = {
         "name": "myLeague",
         "start": "08-30-2019",
         "end": "08-24-2019",
         "startPos": 3000
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('EndBeforeStart' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "The end date of the league can't be before the start date")

   def test_post_league_tooLongDuration(self):
      body = {
         "name": "myLeague",
         "start": "08-24-2018",
         "end": "08-25-2019",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('EndsBeforeStarts' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'Leagues can last a maximum of 1 year')

   def test_post_league(self):
      body = {
         "name": "myLeague",
         "start": "08-24-2018",
         "end": "10-24-2018",
         "startPos": 3000
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)

   def test_post_league_defaultStartPos(self):
      body = {
         "name": "myLeague",
         "start": "08-24-2018",
         "end": "10-24-2018"
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
   

   def tearDown(self):
      self.deleteTables(['League', 'User'])