import requests
from unittest import main

from TestConfiguration import TestConfiguration

class GetInfoTests(TestConfiguration):

   def setUp(self):
      self.headers = {'content-type': 'application/json'}
      self.url = self.base_url + '/appinfo'


   def test_getInfo(self):
      appInfoResponse = requests.get(url=self.url, headers=self.headers)     
      self.assertEqual(appInfoResponse.status_code, 200)

      responseData = self.getJson(appInfoResponse)
   
      self.assertTrue('version' in responseData)
      self.assertTrue('valid' in responseData)
      self.assertTrue(len(responseData) > 0)


if __name__ == "__main__":
   main()
