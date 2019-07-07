import json
import requests
from unittest import main

from TestConfiguration import TestConfiguration


class StockTests(TestConfiguration):
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
		self.url = self.baseUrl + '/stocks/'

	def test_getStock_good(self):
		url = self.url + 'amd'
		response = requests.get(url=url, headers=self.headers)
		responseData = self.getJson(response)
		self.assertEqual(responseData['companyName'], "Advanced Micro Devices, Inc.");

	def test_getStock_nonExistent(self):
		url = self.url + 'FUCK'
		response = requests.get(url=url, headers=self.headers)
		responseData = self.getJson(response)
		self.assertEqual(responseData['UnsupportedTicker'], "The stock ticker is either invalid or unsupported.");

	def tearDown(self):
		self.deleteTables(['Transaction', 'PortfolioItem', 'Portfolio', 'User'])