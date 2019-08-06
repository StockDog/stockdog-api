import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

class GetLeagueTests(TestConfiguration):
    def setUp(self):
        self.headers = {'content-type': 'application/json'}

        # creating a sample user
        registerUrl = self.baseUrl + '/users'
        registerBody = {
           'firstName' : 'Dave',
           'lastName' : 'Janzen',
           'email' : 'dave.janzen18@gmail.com',
           'password' : 'Stockd2g'
        }
        registerResponse = requests.post(url=registerUrl, 
            data=json.dumps(registerBody), headers=self.headers)
        registerResponseData = self.getJson(registerResponse)
        self.assertEqual(registerResponse.status_code, 200)
        self.assertTrue('id' in registerResponseData)
        self.assertTrue(registerResponseData['id'] > 0)
        
        #logging in user
        loginUrl = self.baseUrl + '/users/session'
        loginBody = {
           'email' : 'dave.janzen18@gmail.com',
           'password' : 'Stockd2g'
        }
        loginResponse = requests.post(url=loginUrl, data=json.dumps(loginBody), 
            headers=self.headers)
        loginResponseData = self.getJson(loginResponse)
        self.assertEqual(loginResponse.status_code, 200)
        self.assertIsNotNone(loginResponseData['userId'])
        self.assertIsNotNone(loginResponseData['token'])
        
        self.userId = loginResponseData['userId']
        self.token = loginResponseData['token']
        self.headers['Authorization'] = 'token ' + self.token

        # creating league
        self.leagueBaseUrl = self.baseUrl + '/leagues'
        postLeagueBody = {
            "name": 'test-league',
            "startPos": 5000,
            "start": '01-15-2020',
            "end": '02-15-2020'
        }
        leagueResponse = requests.post(url=self.leagueBaseUrl, 
          data=json.dumps(postLeagueBody), headers=self.headers)
        leagueResponseData = self.getJson(leagueResponse)
        self.assertEquals(leagueResponse.status_code, 200)

        # creating portfolio using the league's invite code
        portfolioUrl = self.baseUrl + '/portfolios'
        postPortfolioBody = {
            "inviteCode": leagueResponseData['inviteCode'],
            "name": 'david'
        }
        portfolioResponse = requests.post(url=portfolioUrl,
            data=json.dumps(postPortfolioBody), headers=self.headers)
        portfolioResponseData = self.getJson(portfolioResponse)
        self.assertEquals(portfolioResponse.status_code, 200)

    def test_get_league(self):
        response = requests.get(url=f"{self.leagueBaseUrl}/1",
            headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(responseData.id, 1)
        self.assertEquals(responseData.startPos, 5000)
        self.assertEquals(responseData.start, "01-15-2020")
        self.assertEquals(responseData.end, "02-15-2020")
        self.assertEquals(responseData.end, "02-15-2020")
        self.assertEquals(len(responseData.portfolios), 1)
        self.assertEquals(responseData.portfolios[0].id, 1)
        self.assertEquals(responseData.portfolios[0].name, "david")
        self.assertEquals(type(responseData.portfolios[0].value), int)

    def test_get_league_non_existant_id(self):
        response = requests.get(url=f"{self.leagueBaseUrl}/2",
            headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 404)

    def tearDown(self):
      self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User'])