import pymysql
import os
import simplejson as json

CONFIG_FILE_PATH = 'Service/db/config.json'
ROOT_FOLDER_NAME = 'stockdog-api/'

def getConfigFilePath():
   cwd = os.getcwd()
   strIdx = cwd.find(ROOT_FOLDER_NAME)
   return cwd[:strIdx + len(ROOT_FOLDER_NAME)] + CONFIG_FILE_PATH


def getDBConn(envType='local'):
   if envType == 'local':
      try:
         configFile = open(getConfigFilePath(), 'r')
         config = json.load(configFile)
         configFile.close()
      except Exception as e:
         raise Exception('The filename was not provided or poorly formatted') 

      conn = pymysql.connect(host='127.0.0.1', user=config['user'], password=config['password'], 
         database=config['database'], cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   else:
      conn = pymysql.connect(host='127.0.0.1', user='root', password='', 
         database='StockDog', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   
   return conn
