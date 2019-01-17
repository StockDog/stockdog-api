import requests
import simplejson
from unittest import TestCase
import sys

sys.path.append('../')
from Service.src.util.logger import Logger
from Service.src.util.db_connection import getDBConn

TRAVIS_ENV = 'travis'
TRAVIS_URL = "http://0.0.0.0:5005/api"

LOCAL_ENV = 'local'
LOCAL_URL = 'http://localhost:5005/api'

class TestConfiguration(TestCase):

   @classmethod
   def setUpClass(self):
      self.log = Logger(True, True, True)
      try:
         self.db = getDBConn(LOCAL_ENV)
         self.cursor = self.db.cursor()
      except Exception as e:
         self.log.error(e)
         raise e

      self.headers = {'content-type' : 'application/json'}
      self.baseUrl = LOCAL_URL

   
   def getJson(self, res):
      try:
         return res.json()
      except simplejson.errors.JSONDecodeError as e:
         return None


   def deleteTables(self, tables, resetAutoIncrement=True):
      for table in tables:
         self.cursor.execute("DELETE FROM " + table)
         if resetAutoIncrement:
            self.cursor.execute("ALTER TABLE " + table + " AUTO_INCREMENT=1")

   
   @classmethod
   def tearDownClass(self):
      tables = ['User']
      for table in tables:
         self.cursor.execute("DELETE FROM " + table)
         self.cursor.execute("ALTER TABLE " + table + " AUTO_INCREMENT=1")

      if getattr(self, 'db', None) is not None:
         self.db.close()
      