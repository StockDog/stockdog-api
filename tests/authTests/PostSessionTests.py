import sys
import json
from unittest import main
import requests

from TestConfiguration import TestConfiguration

class PostSessionTests(TestConfiguration):

   def setUp(self):
      self.headers = {'content-type' : 'application/json'}
      self.url = self.baseUrl + '/users/session'
      
      url = self.baseUrl + '/users'
      body = {
         'firstName' : 'Dave',
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      response = requests.post(url=url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEqual(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)


   def test_login_user_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      body = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_login_user_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      body = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_login_user(self):
      body = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 200)
      self.assertTrue('userId' in responseData)
      self.assertTrue(responseData['userId'] > 0)
      self.assertTrue('token' in responseData)
      self.assertTrue(responseData['token'] != "")


   def test_login_user_twice(self):
      body = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }
      loginResponse1 = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      loginResponse1Data = self.getJson(loginResponse1)
      
      loginResponse2 = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      loginResponse2Data = self.getJson(loginResponse2)

      self.assertEquals(loginResponse1Data, loginResponse2Data)


   def test_login_user_noEmail(self):
      body = {
         'password' : 'Stockd2g'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'email is a required field')      
   

   def test_login_user_noPassword(self):
      body = {
         'email' : 'dave.janzen18@gmail.com'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'password is a required field')      
   

   def test_login_user_noBody(self):
      body = {
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertEquals(len(responseData), 2)
   

   def test_login_user_invalidEmail(self):
      body = {
         'email' : 'dave.janzegmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'email is an invalid address')
      

   def test_login_user_nonExistentEmail(self):
      body = {
         'email' : 'steph.curry@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('NonexistentUser' in responseData)
      self.assertEquals(responseData['NonexistentUser'], 'User does not exist.')
   

   def test_login_user_wrongPassword(self):
      body = {
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd1g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 401)
      self.assertTrue('PasswordMismatch' in responseData)
      self.assertEquals(responseData['PasswordMismatch'], 'Incorrect password for user.')
   

   def tearDown(self):
      self.deleteTables(['User'])
