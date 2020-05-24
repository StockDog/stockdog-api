import simplejson
from unittest import TestCase
import sys

sys.path.append('../')
from util.logger import Logger
from util.db_connection import getDBConn

TRAVIS_ENV = 'travis'
TRAVIS_URL = "http://0.0.0.0:5005/api/v1.0"

LOCAL_ENV = 'local'
LOCAL_URL = 'http://localhost:5005/api/v1.0'

class TestConfiguration(TestCase):

   @classmethod
   def setUpClass(self):
      self.log = Logger(True, True, True)
      try:
         self.db = getDBConn()
         self.cursor = self.db.cursor()
      except Exception as e:
         self.log.error(e)
         raise e

      self.headers = {'Content-Type' : 'application/json'}
      self.base_url = TRAVIS_URL

   
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
      