import requests

from tests.TestConfiguration import TestConfiguration
from tests.test_helper_functions import register_david_janzen, login_david_janzen
from datetime import datetime


class GetLeagueInviteCodesTests(TestConfiguration):
    def setUp(self):
        self.headers = {'content-type': 'application/json'}

        register_data = register_david_janzen(self.base_url, self.headers)
        self.assertTrue('id' in register_data)
        self.assertTrue(register_data['id'] > 0)

        login_data = login_david_janzen(self.base_url, self.headers)
        self.assertIsNotNone(login_data['userId'])
        self.assertIsNotNone(login_data['token'])
        self.headers['Authorization'] = 'token ' + login_data['token']

        # Create multiple leagues
        # Have to do it through the database because it breaks api rules for creating new leagues
        DATE_FORMAT = "%m-%d-%Y"

        self.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
                            "VALUES (%s, %s, %s, %s, %s, %s)", [
                                'testLeague1',
                                datetime.strptime('01-15-2025', DATE_FORMAT),
                                datetime.strptime('01-15-2026', DATE_FORMAT),
                                2500,
                                "abc",
                                0
                            ])

        self.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
                            "VALUES (%s, %s, %s, %s, %s, %s)", [
                                'testLeague2',
                                datetime.strptime('07-07-2019', DATE_FORMAT),
                                datetime.strptime('07-07-2029', DATE_FORMAT),
                                800,
                                "def",
                                0
                            ])

        self.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
                            "VALUES (%s, %s, %s, %s, %s, %s)", [
                                'testLeague3',
                                datetime.strptime('11-20-2018', DATE_FORMAT),
                                datetime.strptime('12-30-2018', DATE_FORMAT),
                                43000,
                                "ghi",
                                0
                            ])

        self.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
                            "VALUES (%s, %s, %s, %s, %s, %s)", [
                                'testLeague4',
                                datetime.strptime('03-15-2024', DATE_FORMAT),
                                datetime.strptime('02-15-2025', DATE_FORMAT),
                                10000,
                                "jkl",
                                0
                            ])

        self.url = self.base_url + '/leagues'

    def test_get_league_invite_codes(self):
        res = requests.get(url=self.url, headers=self.headers)
        self.assertTrue(res.status_code, 200)

        data = res.json()
        self.assertEquals(len(data), 4)

        self.assertEquals(data[0]['id'], 1)
        self.assertEquals(data[1]['id'], 2)
        self.assertEquals(data[2]['id'], 3)
        self.assertEquals(data[3]['id'], 4)

        self.assertEquals(data[0]['name'], 'testLeague1')
        self.assertEquals(data[0]['startPos'], 2500)
        self.assertEquals(data[0]['start'], '01-15-2025')
        self.assertEquals(data[0]['end'], '01-15-2026')
        self.assertEquals(data[0]['status'], 'planned')
        self.assertEquals(data[0]['inviteCode'], 'abc')

        self.assertEquals(data[1]['name'], 'testLeague2')
        self.assertEquals(data[1]['startPos'], 800)
        self.assertEquals(data[1]['start'], '07-07-2019')
        self.assertEquals(data[1]['end'], '07-07-2029')
        self.assertEquals(data[1]['status'], 'active')
        self.assertEquals(data[1]['inviteCode'], 'def')

        self.assertEquals(data[2]['name'], 'testLeague3')
        self.assertEquals(data[2]['startPos'], 43000)
        self.assertEquals(data[2]['start'], '11-20-2018')
        self.assertEquals(data[2]['end'], '12-30-2018')
        self.assertEquals(data[2]['status'], 'ended')
        self.assertEquals(data[2]['inviteCode'], 'ghi')

        self.assertEquals(data[3]['name'], 'testLeague4')
        self.assertEquals(data[3]['startPos'], 10000)
        self.assertEquals(data[3]['start'], '03-15-2024')
        self.assertEquals(data[3]['end'], '02-15-2025')
        self.assertEquals(data[3]['status'], 'planned')
        self.assertEquals(data[3]['inviteCode'], 'jkl')

    def tearDown(self):
        self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User', 'League'])