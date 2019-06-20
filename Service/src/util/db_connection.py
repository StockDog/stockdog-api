import pymysql
import os
import simplejson as json

CONFIG_FILE_PATH = './config.json'

def getDBConn(envType='local'):
   if envType == 'local':
      try:
         configFile = open(CONFIG_FILE_PATH, 'r')
         config = json.load(configFile)
         configFile.close()
      except Exception as e:
         raise Exception('The db config filename was not provided or poorly formatted') 

      conn = pymysql.connect(host='127.0.0.1', user=config['db']['user'], password=config['db']['password'], 
         database=config['db']['database'], cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   else:
      conn = pymysql.connect(host='127.0.0.1', user='root', password='', 
         database='StockDog', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   
   return conn
