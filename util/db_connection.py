import pymysql
import os

def getDBConn():
   conn = pymysql.connect(host='127.0.0.1', user="sduser", password="sdpass",
      database="StockDog", cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   
   return conn
