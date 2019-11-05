import pymysql
import os
from .config import getConfig

def getDBConn(envType='local'):
   if envType == 'local':
      config = getConfig()

      conn = pymysql.connect(host='127.0.0.1', user=config['db']['user'], password=config['db']['password'], 
         database=config['db']['database'], cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   else:
      conn = pymysql.connect(host='127.0.0.1', user='sduser', password='sdpass', 
         database='StockDog', cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   
   return conn
