import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, login_david_janzen, register_david_janzen, create_portfolio


class PostDeletePortfolioTests(TestConfiguration):
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json',
            'App-Version': '*'
        }

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

        init_buy_power = responseData['buyPower']

        # Makes sure that the portfolio history is included
        # This depends on the portfolio GET requests
        response = requests.get(url=self.url + '/' + str(responseData['id']), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(len(responseData['history']), 1)
        self.assertEquals(responseData['history'][0]['value'], responseData['buyPower'])

    def test_post_portfolio_multiple_same_league(self):
        resP1 = requests.post(url=self.url, data=json.dumps({"name": 'p1', 'inviteCode': self.invite_code}),
                              headers=self.headers)
        self.assertEquals(resP1.status_code, 200)

        resP2 = requests.post(url=self.url, data=json.dumps({"name": 'p2', 'inviteCode': self.invite_code}),
                              headers=self.headers)
        self.assertEquals(resP2.status_code, 403)

    def test_post_portfolio_joinLeague(self):
        league_data_1 = create_league(self.base_url, self.headers)
        league_data_2 = create_league(self.base_url, self.headers)
        league_data_3 = create_league(self.base_url, self.headers)

        resP1 = requests.post(url=self.url, data=json.dumps({"name": 'p1', 'inviteCode': league_data_1['inviteCode']}),
            headers=self.headers)
        self.assertEquals(resP1.status_code, 200)

        resP2 = requests.post(url=self.url, data=json.dumps({"name": 'p2', 'inviteCode': league_data_2['inviteCode']}),
            headers=self.headers)
        self.assertEquals(resP2.status_code, 200)

        resP3 = requests.post(url=self.url, data=json.dumps({"name": 'p3', 'inviteCode': league_data_3['inviteCode']}),
            headers=self.headers)
        self.assertEquals(resP3.status_code, 200)

        resGet = requests.get(url=self.url, headers=self.headers)
        resGetData = self.getJson(resGet)
        self.assertEquals(len(resGetData), 3)

        # Now do the delete
        resDel = requests.delete(url=self.url + "/" + str(self.getJson(resP2)["id"]), headers=self.headers)

        # Check to see if deleted
        resGet = requests.get(url=self.url, headers=self.headers)
        resGetData = self.getJson(resGet)

        self.assertEquals(len(resGetData), 2)
        self.assertEquals(resGetData[0]["id"], self.getJson(resP1)["id"])
        self.assertEquals(resGetData[1]["id"], self.getJson(resP3)["id"])


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
        self.headers.pop('Content-Type')
        body = {
            'name': 'mynewportfolio',
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('MissingHeader' in responseData[0])
        self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")

    def test_post_portfolio_invalidContentTypeHeader(self):
        self.headers['Content-Type'] = 'plain/text'
        body = {
            'name': 'mynewportfolio',
        }

        response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 400)
        self.assertTrue('InvalidHeader' in responseData[0])
        self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of ['application/json']")

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
        self.deleteTables(['League', 'Portfolio', 'User', 'PortfolioHistory'])

    if __name__ == "__main__":
        main()
