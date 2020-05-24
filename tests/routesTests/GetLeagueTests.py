import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration

from tests.test_helper_functions import create_league, register_david_janzen, login_david_janzen, create_portfolio


class GetLeagueTests(TestConfiguration):
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

        portfolio_data = create_portfolio(
            self.base_url, self.headers, league_data['inviteCode'])
        self.assertTrue('id' in portfolio_data)
        self.assertTrue(portfolio_data['id'] > 0)
        self.assertTrue('buyPower' in portfolio_data)
        self.assertEquals(portfolio_data['buyPower'], 5000)

        self.portfolioId = portfolio_data['id']
        self.invite_code = league_data['inviteCode']
        self.url = self.base_url + '/portfolios'

        # Manually add leagues that aren't in the acceptable date range
        self.cursor.execute(
            'INSERT INTO League(name, start, end, startPos, inviteCode, ' +
            'ownerId) ' +
            'VALUES("plannedleague", "2100-01-01", "2110-01-01",' +
            ' 1000, "ic1", %s)', [register_data["id"]])
        self.planned_league_id = self.cursor.lastrowid

        self.cursor.execute(
            'INSERT INTO League(name, start, end, startPos, inviteCode, ' +
            'ownerId) ' +
            'VALUES("endedleague", "2020-02-22", "2020-02-27",' +
            ' 1000, "ic2", %s)', [register_data["id"]])
        self.ended_league_id = self.cursor.lastrowid

        self.cursor.execute(
            'INSERT INTO League(name, start, end, startPos, inviteCode, ' +
            'ownerId) ' +
            'VALUES("activeleague", "1900-01-01", "2100-01-01",' +
            ' 1000, "ic3", %s)', [register_data["id"]])
        self.active_league_id = self.cursor.lastrowid

    def test_get_league(self):
        response = requests.get(url=f"{self.base_url}/leagues/1",
                                headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(responseData["id"], 1)
        self.assertEquals(responseData["name"], "test-league")
        self.assertEquals(responseData["startPos"], 5000)
        self.assertEquals(responseData["start"],
                          "Fri, 15 Jan 2021 00:00:00 GMT")
        self.assertEquals(responseData["end"], "Mon, 15 Feb 2021 00:00:00 GMT")
        self.assertEquals(len(responseData["portfolios"]), 1)
        self.assertEquals(responseData["portfolios"][0]["id"], 1)
        self.assertEquals(responseData["portfolios"]
                          [0]["name"], "mynewportfolio")
        self.assertEquals(type(responseData["portfolios"][0]["value"]), float)
        self.assertEquals(responseData["inviteCode"], self.invite_code)
        self.assertIsNotNone(responseData['status'])

    def test_planned_league(self):
        response = requests.get(
            url=f"{self.base_url}/leagues/{self.planned_league_id}",
            headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(responseData["status"], "planned")

    def test_ended_league(self):
        response = requests.get(
            url=f"{self.base_url}/leagues/{self.ended_league_id}",
            headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(responseData["status"], "ended")

    def test_active_league(self):
        response = requests.get(
            url=f"{self.base_url}/leagues/{self.active_league_id}",
            headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(responseData["status"], "active")

    def test_get_league_non_existant_id(self):
        response = requests.get(url=f"{self.base_url}/leagues/243",
                                headers=self.headers)
        responseData = self.getJson(response)

        self.assertEquals(response.status_code, 404)

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem',
                           'Portfolio', 'User', 'League', 'PortfolioHistory'])
