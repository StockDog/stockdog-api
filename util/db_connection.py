import pymysql
import os

def getDBConn():
   host = os.getenv("db.host") or "127.0.0.1"
   user = os.getenv("db.user") or "sduser"
   password = os.getenv("db.password") or "sdpass"
   database = os.getenv("db.database") or "StockDog"

   conn = pymysql.connect(host=host, user=user, password=password,
                          database=database, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
   return conn
