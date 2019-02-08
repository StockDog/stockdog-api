import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class PostPortfolioTests(TestConfiguration):
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

      leagueUrl = self.baseUrl + '/leagues'
      leagueBody = {
         "name": "AverageTraderJoes",
         "start": "08-24-2019",
         "end": "08-30-2019",
         "startPos": 3000
      }
      leagueResponse = requests.post(leagueUrl, data=json.dumps(leagueBody), headers=self.headers)
      leagueResponseData = self.getJson(leagueResponse)      
      self.assertEquals(leagueResponse.status_code, 200)
      self.assertIsNotNone(leagueResponseData['id'])
      self.assertIsNotNone(leagueResponseData['inviteCode'])
      self.assertIsNotNone(leagueResponseData['startPos'])

      self.leagueId = leagueResponseData['id']
      self.inviteCode = leagueResponseData['inviteCode']
      self.leagueStartPos = leagueResponseData['startPos']

      self.url = self.baseUrl + '/portfolios'


   def test_post_portfolio_joinLeague(self):
      body = {
         'name' : 'techtothemoon',
         'inviteCode': self.inviteCode
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
      self.assertTrue('buyPower' in responseData)
      self.assertEquals(responseData['buyPower'], self.leagueStartPos)
      self.assertTrue('leagueId' in responseData)
      self.assertEquals(responseData['leagueId'], self.leagueId)
      self.assertTrue('leagueName' in responseData)
      self.assertEquals(responseData['leagueName'], "AverageTraderJoes")

      
   def test_post_portfolio_joinLeagueWithDifferentBuyPower(self):
      body = {
         'name' : 'techtothemoon',
         'inviteCode': self.inviteCode,
         'buyPower': 1000
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
      self.assertTrue('buyPower' in responseData)
      self.assertEquals(responseData['buyPower'], self.leagueStartPos)
      self.assertTrue('leagueId' in responseData)
      self.assertEquals(responseData['leagueId'], self.leagueId)
      self.assertTrue('leagueName' in responseData)
      self.assertEquals(responseData['leagueName'], "AverageTraderJoes")


   def test_post_portfolio_joinLeagueWrongInviteCode(self):
      body = {
         'name' : 'techtothemoon',
         'inviteCode': "SWC434"
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InviteCodeMismatch' in responseData)
      self.assertEquals(responseData['InviteCodeMismatch'], "The invite code provided does not match any existing league")


   def test_post_portfolio_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      body = {
         'name' : 'mynewportfolio',
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_post_portfolio_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      body = {
         'name' : 'mynewportfolio',
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")

   def test_post_portfolio_soloDefaultBuyPower(self):
      body = {
         'name' : 'mynewportfolio',
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
      self.assertTrue('buyPower' in responseData)
      self.assertEquals(responseData['buyPower'], 10000)


   def test_post_portfolio_soloCustomBuyPower(self):
      body = {
         'name' : 'mynewportfolio',
         'buyPower' : 300000
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
      self.assertTrue('buyPower' in responseData)
      self.assertEquals(responseData['buyPower'], 300000)
   

   def test_post_portfolio_notLoggedIn(self):
      logoutUrl = self.baseUrl + '/users/' + str(self.userId) + '/session'
      logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)     
      self.assertEqual(logoutResponse.status_code, 200)

      body = {
         'name' : 'anotherportfolio'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 401)
      self.assertTrue('NotLoggedIn' in responseData)
      self.assertTrue(responseData['NotLoggedIn'], 'User must be logged in.')


   def test_post_portfolio_soloNoName(self):
      body = {
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'name is a required field')


   def test_post_portfolio_soloLongName(self):
      body = {
         'name' : 'thisshouldbeoverthecharacterlimitbecausethelimitis32'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'name is too long - must be under 32 characters')


   def test_post_portfolio_soloEmptyName(self):
      body = {
         'name' : ''
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'name must not be empty')


   def test_post_portfolio_soloInvalidName(self):
      body = {
         'name' : 2121342
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'name is not a string or formatted incorrectly')
   

   def test_post_portfolio_soloNegativeBuyPower(self):
      body = {
         'name' : 'techtothemooon',
         'buyPower' : -2000
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'buyPower must be an integer greater than 1 and less than 1000000')

   
   def test_post_portfolio_soloHighBuyPower(self):
      body = {
         'name' : 'techtothemooon',
         'buyPower' : 20000000000
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'buyPower must be an integer greater than 1 and less than 1000000')


   def tearDown(self):
      self.deleteTables(['League', 'Portfolio', 'User'])

   
   if __name__ == "__main__":
      main()