import requests
import simplejson as json
from unittest import main

from TestConfiguration import TestConfiguration

class PostUserTests(TestConfiguration):

   def setUp(self):
      self.headers = {'content-type' : 'application/json'}
      self.url = self.base_url + '/users'


   def test_register_user_missingContentTypeHeader(self):
      self.headers.pop('content-type')
      body = {
         'firstName' : 'Dave',
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'StockD2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingHeader' in responseData[0])
      self.assertEquals(responseData[0]['MissingHeader'], "Content-Type is a required header")


   def test_register_user_invalidContentTypeHeader(self):
      self.headers['content-type'] = 'plain/text'
      body = {
         'firstName' : 'Dave',
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'StockD2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidHeader' in responseData[0])
      self.assertEquals(responseData[0]['InvalidHeader'], "API only accepts Content-Type of application/json")


   def test_register_user(self):
      body = {
         'firstName' : 'Dave',
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'StockD2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)

   
   def test_register_user_noFirstName(self):
      body = {
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'firstName is a required field')


   def test_register_user_noLastName(self):
      body = {
         'firstName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'lastName is a required field')

   
   def test_register_user_noEmail(self):
      body = {
         'firstName' : 'Janzen',
         'lastName' : 'Barkley',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'email is a required field')



   def test_register_user_noPassword(self):
      body = {
         'firstName' : 'Janzen',
         'lastName' : 'Barkley',
         'email' : 'dave.janzen18@gmail.com'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 400)
      self.assertTrue('MissingField' in responseData[0])
      self.assertEquals(responseData[0]['MissingField'], 'password is a required field')


   def test_register_user_noBody(self):
      body = {
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertEquals(len(responseData), 4)


   def test_register_user_invalidFirstName(self):
      body = {
         'firstName' : 14321,
         'lastName' : 'Janzen',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'firstName is not a string or formatted incorrectly')
   

   def test_register_user_invalidLastName(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : False,
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'lastName is not a string or formatted incorrectly')
   

   def test_register_user_invalidEmail(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzegmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'email is an invalid address')


   def test_register_user_invalidPassword_noNumbers(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'NoNumber'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "password must have 8 characters, 1 uppercase letter " +
         "1 lowercase letter, and 1 number")
   

   def test_register_user_invalidPassword_noLetters(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzen18@gmail.com',
         'password' : '12345678'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "password must have 8 characters, 1 uppercase letter " +
         "1 lowercase letter, and 1 number")
   

   def test_register_user_invalidPassword_tooShort(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'hi1A'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "password must have 8 characters, 1 uppercase letter " +
         "1 lowercase letter, and 1 number")
   
   
   def test_register_user_invalidPassword_lowercaseOnly(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'abcdefghijk13'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "password must have 8 characters, 1 uppercase letter " +
         "1 lowercase letter, and 1 number")
   
   
   def test_register_user_invalidPassword_UppercaseOnly(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'ABCDEFGHI131'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], "password must have 8 characters, 1 uppercase letter " +
         "1 lowercase letter, and 1 number")
   

   def test_register_user_longFirstName(self):
      body = {
         'firstName' : 'DavisoneDavisoneDavisoneDavisoneD',
         'lastName' : 'James',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
   
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'firstName is too long - must be under 32 characters')
   

   def test_register_user_longLastName(self):
      body = {
         'firstName' : 'Davisone',
         'lastName' : 'JamesJamesJamesJamesJamesJamesJames',
         'email' : 'dave.janzen18@gmail.com',
         'password' : 'Stockd2g'
      }

      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)
      
      self.assertEquals(response.status_code, 400)
      self.assertTrue('InvalidField' in responseData[0])
      self.assertEquals(responseData[0]['InvalidField'], 'lastName is too long - must be under 32 characters')
   

   def test_register_user_duplicateEmail(self):
      body = {
         'firstName' : 'Davison',
         'lastName' : 'Fuller',
         'email' : 'dave.fuler@gmail.com',
         'password' : 'normaLpas1'
      }
      response = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseData = self.getJson(response)

      self.assertEquals(response.status_code, 200)
      self.assertTrue('id' in responseData)
      self.assertTrue(responseData['id'] > 0)
   
      responseDuplicate = requests.post(url=self.url, data=json.dumps(body), headers=self.headers)
      responseDuplicateData = self.getJson(responseDuplicate)
      
      self.assertEquals(responseDuplicate.status_code, 400)
      self.assertTrue('DuplicateEmail' in responseDuplicateData)
      self.assertEquals(responseDuplicateData['DuplicateEmail'], 'User with email already exists.')
   
   
   def tearDown(self):
      self.deleteTables(['User'])


if __name__ == "__main__":
   main()