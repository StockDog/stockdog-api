import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_portfolio, create_league, login_david_janzen, register_david_janzen


class PostLeagueTests(TestConfiguration):
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

        self.url = self.base_url + '/leagues'
        self.userId = login_data['userId']

    def test_post_league_missingContentTypeHeade(self):
        self.headers.pop('content-type')
        body = {
            "name": "myLeague",
            "start": "08-24-2029",
            "end": "08-30-2029",
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
            "start": "08-24-2029",
            "end": "08-30-2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidHeader' in responseData[0])
        self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")

    def test_post_league_notLoggedIn(self):
        logoutUrl = self.base_url + '/users/' + str(self.userId) + '/session'
        logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
        self.assertEqual(logoutResponse.status_code, 200)

        body = {
            "name": "myLeague",
            "start": "08-24-2029",
            "end": "08-30-2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 401)
        self.assertTrue('NotLoggedIn' in responseData)
        self.assertTrue(responseData['NotLoggedIn'], 'User must be logged in.')

    def test_post_league_missingName(self):
        body = {
            "start": "08-24-2029",
            "end": "08-30-2029",
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
            "end": "08-30-2029",
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
            "start": "08-30-2029",
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
            "start": "08-24-2029",
            "end": "08-30-2029",
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
            "start": "08-24-2029",
            "end": "08-30-2029",
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
            "start": "08/24/2029",
            "end": "08-30-2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'start date must be a valid day in MM-DD-YYYY format')

    def test_post_league_invalidEnd(self):
        body = {
            "name": 'myLeague',
            "start": "08-24-2029",
            "end": "08/30/2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'end date must be a valid day in MM-DD-YYYY format')

    def test_post_league_invalidStartDay(self):
        body = {
            "name": 'myLeague',
            "start": "08-35-2029",
            "end": "09-12-2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'start date must be a valid day in MM-DD-YYYY format')

    def test_post_league_negativeStartPos(self):
        body = {
            "name": 'myLeague',
            "start": "08-24-2029",
            "end": "08-30-2029",
            "startPos": -3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'],
                          'startPos must be an integer greater than 1 and less than 1000000')

    def test_post_league_highStartPos(self):
        body = {
            "name": 'myLeague',
            "start": "08-24-2029",
            "end": "08-30-2029",
            "startPos": 300000000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'],
                          'startPos must be an integer greater than 1 and less than 1000000')

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
        self.assertEquals(responseData[0]['InvalidField'], "start date can't be in the past")

    def test_post_league_pastEndDate(self):
        body = {
            "name": 'myLeague',
            "start": "08-24-2029",
            "end": "04-30-2018",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], "end date can't be in the past")

    def test_post_league_endBeforeStart(self):
        body = {
            "name": "myLeague",
            "start": "08-30-2029",
            "end": "08-24-2029",
            "startPos": 3000
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('EndBeforeStart' in responseData)
        self.assertEquals(responseData['EndBeforeStart'], "The end date can not be before the start date")

    def test_post_league_tooLongDuration(self):
        body = {
            "name": "myLeague",
            "start": "08-24-2029",
            "end": "08-25-2030",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('LeagueDurationTooLong' in responseData)
        self.assertEquals(responseData['LeagueDurationTooLong'], 'Leagues can last a maximum of 1 year')

    def test_post_league(self):
        body = {
            "name": "myLeague",
            "start": "08-24-2029",
            "end": "10-24-2029",
            "startPos": 3000
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('id' in responseData)
        self.assertTrue(responseData['id'] > 0)
        self.assertTrue('inviteCode' in responseData)
        self.assertTrue(len(responseData['inviteCode']) > 0)
        self.assertTrue('startPos' in responseData)
        self.assertEqual(responseData['startPos'], 3000)

    def test_post_league_defaultStartPos(self):
        body = {
            "name": "myLeague",
            "start": "08-24-2029",
            "end": "10-24-2029"
        }
        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('id' in responseData)
        self.assertTrue(responseData['id'] > 0)
        self.assertTrue('inviteCode' in responseData)
        self.assertTrue(len(responseData['inviteCode']) > 0)
        self.assertTrue('startPos' in responseData)
        self.assertEqual(responseData['startPos'], 10000)

    def tearDown(self):
        self.deleteTables(['League', 'User', 'Portfolio'])
