from flask import Blueprint, abort
from urllib.parse import urlencode
from pprint import pprint
from werkzeug.exceptions import *
from datetime import date, timedelta, datetime

import json
import requests
import re
import operator

stock_api = Blueprint('stock_api', __name__)

@stock_api.errorhandler(400)
@stock_api.errorhandler(404)
def malformed_request(error):
   if isinstance(error, BadRequest):
      return 'Request was formed incorrectly. ' + \
         'Valid lengths are day, week, month, year.', 400
   elif isinstance(error, NotFound):
      return 'Request was formed incorrectly. ' + \
         'The stock ticker is either invalid or unsupported.', 404
   else:
      return 'Something went wrong...', 400


@stock_api.route('/api/stock/<ticker>/history/<length>')
def get_history(ticker, length):
   try:
      function = getFunction(length)
      outputSize = getOutputSize(length)
   except Exception as e:
      abort(400)

   interval = getInterval(length)
   apiKey = getApiKey()

   queryParams = {
      'function' : function,
      'symbol' : ticker,
      'outputsize' : outputSize,
      'apikey' : apiKey
   }

   if interval:
      queryParams['interval'] = interval

   alphaVantageApi = 'https://www.alphavantage.co/query?'
   response = (requests.get(alphaVantageApi + urlencode(queryParams))).json()
   
   if response.get('Error Message'):
      abort(404)

   data = formatData(response, interval, length)

   return json.dumps(data)
    

def getFunction(length):
   if length == 'day' or length == 'week':
      return 'TIME_SERIES_INTRADAY'
   elif length == 'month' or length == 'year':
      return 'TIME_SERIES_DAILY'
   else:
      raise Exception('Invalid length provided')


def getOutputSize(length):
   if length == 'day' or length == 'month':
      return 'compact'
   elif length == 'week' or length == 'year':
      return 'full'
   else:
      raise Exception('Invalid length provided') 


def getInterval(length):
   if length == 'day':
      return '5min'
   elif length == 'week':
      return '15min'
   elif length == 'month' or length == 'year':
      return ''


def getApiKey():
   return '3UCU111LQLB5581W'


def getLastWeekday():
   today = date.today()
   if date.today().weekday() <= 4:
      return today
   else:
      dayBefore = today - timedelta(days=1)
      while dayBefore.weekday() > 4:
         dayBefore -= timedelta(days=1)

      return dayBefore


def formatData(jsonData, interval, length):
   if not interval:
      interval = 'Daily'

   timeSeriesData = jsonData['Time Series (' + interval + ')']

   slicedTimeSeriesData = []

   if length == 'day':
      slicedTimeSeriesData = formatDayData(timeSeriesData)
      pprint(slicedTimeSeriesData)
   elif length == 'week':
      return 1
   elif length == 'month':
      return 1
   elif length == 'year':
      return 1
   else:
      raise Exception('Invalid length provided')

   return slicedTimeSeriesData

def formatDayData(timeSeriesData):
   slicedTimeSeriesData = []

   for (key, value) in timeSeriesData.items():
      day = getLastWeekday()
      strDate = day.strftime('%Y-%m-%d')
      if strDate in key:
         slicedTimeSeriesData.append(
            {
               'time' : datetime.strptime(key, '%Y-%m-%d %H:%M:%S').timestamp(),
               'price' : value['1. open']
            }
         )

   slicedTimeSeriesData.sort(key=lambda item:item['time'], reverse=True)
   return slicedTimeSeriesData











