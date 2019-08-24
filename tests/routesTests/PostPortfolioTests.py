import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, login_david_janzen, register_david_janzen, create_portfolio


class PostPortfolioTests(TestConfiguration):
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

        self.user_id = login_data['userId']

        self.league_id = league_data['id']
        self.invite_code = league_data['inviteCode']
        self.league_start_pos = league_data['startPos']

        self.url = self.base_url + '/portfolios'

    def test_post_portfolio_joinLeague(self):
        body = {
            'name': 'techtothemoon',
            'inviteCode': self.invite_code
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('id' in responseData)
        self.assertTrue(responseData['id'] > 0)
        self.assertTrue('buyPower' in responseData)
        self.assertEquals(responseData['buyPower'], self.league_start_pos)
        self.assertTrue('leagueId' in responseData)
        self.assertEquals(responseData['leagueId'], self.league_id)
        self.assertTrue('leagueName' in responseData)
        self.assertEquals(responseData['leagueName'], "test-league")

    def test_post_portfolio_joinLeagueWithDifferentBuyPower(self):
        body = {
            'name': 'techtothemoon',
            'inviteCode': self.invite_code,
            'buyPower': 1000
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('id' in responseData)
        self.assertTrue(responseData['id'] > 0)
        self.assertTrue('buyPower' in responseData)
        self.assertEquals(responseData['buyPower'], self.league_start_pos)
        self.assertTrue('leagueId' in responseData)
        self.assertEquals(responseData['leagueId'], self.league_id)
        self.assertTrue('leagueName' in responseData)
        self.assertEquals(responseData['leagueName'], "test-league")

    def test_post_portfolio_joinLeagueWrongInviteCode(self):
        body = {
            'name': 'techtothemoon',
            'inviteCode': "SWC434"
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InviteCodeMismatch' in responseData)
        self.assertEquals(responseData['InviteCodeMismatch'],
                          "The invite code provided does not match any existing league")

    def test_post_portfolio_missingContentTypeHeader(self):
        self.headers.pop('content-type')
        body = {
            'name': 'mynewportfolio',
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('MissingHeader' in responseData[0])
        self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")

    def test_post_portfolio_invalidContentTypeHeader(self):
        self.headers['content-type'] = 'plain/text'
        body = {
            'name': 'mynewportfolio',
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidHeader' in responseData[0])
        self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")

    def test_post_portfolio_soloDefaultBuyPower(self):
        body = {
            'name': 'mynewportfolio',
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
            'name': 'mynewportfolio',
            'buyPower': 300000
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('id' in responseData)
        self.assertTrue(responseData['id'] > 0)
        self.assertTrue('buyPower' in responseData)
        self.assertEquals(responseData['buyPower'], 300000)

    def test_post_portfolio_notLoggedIn(self):
        logoutUrl = self.base_url + '/users/' + str(self.user_id) + '/session'
        logoutResponse = requests.delete(url=logoutUrl, headers=self.headers)
        self.assertEqual(logoutResponse.status_code, 200)

        body = {
            'name': 'anotherportfolio'
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
            'name': 'thisshouldbeoverthecharacterlimitbecausethelimitis32'
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'name is too long - must be under 32 characters')

    def test_post_portfolio_soloEmptyName(self):
        body = {
            'name': ''
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'name must not be empty')

    def test_post_portfolio_soloInvalidName(self):
        body = {
            'name': 2121342
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'], 'name is not a string or formatted incorrectly')

    def test_post_portfolio_soloNegativeBuyPower(self):
        body = {
            'name': 'techtothemooon',
            'buyPower': -2000
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'],
                          'buyPower must be an integer greater than 1 and less than 1000000')

    def test_post_portfolio_soloHighBuyPower(self):
        body = {
            'name': 'techtothemooon',
            'buyPower': 20000000000
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidField' in responseData[0])
        self.assertEquals(responseData[0]['InvalidField'],
                          'buyPower must be an integer greater than 1 and less than 1000000')

    def tearDown(self):
        self.deleteTables(['League', 'Portfolio', 'User'])

    if __name__ == "__main__":
        main()
