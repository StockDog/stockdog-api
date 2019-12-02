import os

from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, Response, g
import requests
import simplejson as json
import time

from auth import auth
from request_validator import validator
from request_validator.schemas import charts_schema
from util.error_map import errors

WEEK = '5d'
MONTH = '1m'
YEAR = '1y'

IEX_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
IEX_DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

stock_api = Blueprint('stock_api', __name__)

IEX_URL_PREFIX = 'https://cloud.iexapis.com/v1/stock/'

@stock_api.route('/api/v1.0/stocks/<ticker>', methods=['GET'])
@auth.login_required
def getStock(ticker):
   try:
      stockInformation = getStockInformation(ticker)
      stockInformation['currentPrice'] = getSharePrice(ticker)
   except requests.HTTPError as e:
      return handleIexError(e)

   return json.dumps(stockInformation)

def getStockInformation(ticker):
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/company?token={os.getenv("iexToken")}'

   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   if (rawResponse.status_code != 200):
      rawResponse.raise_for_status()

   response = rawResponse.json()

   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return response

# Returns a dict of stock information
def getStockInformations(tickers):
   tickersDelimited = ','.join(tickers)
   requestUrl = f'https://cloud.iexapis.com/stable/stock/market/company?symbols={tickersDelimited}&token={os.getenv("iexToken")}'
   
   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   if (rawResponse.status_code != 200):
      rawResponse.raise_for_status()

   response = rawResponse.json()

   # Converting to dictionary because it is better
   infoDict = {}
   for stock in response:
      infoDict[stock['symbol']] = stock

   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return infoDict

@stock_api.route('/api/v1.0/stocks/<ticker>/chart', methods=['GET'])
@auth.login_required
@validator.validate_params(charts_schema.fields)
def extract_args(ticker):
   length = request.args.get('length')

   try:
      history = get_history(ticker, length)
   except requests.HTTPError as e:
      return handleIexError(e)

   return json.dumps(history)


def get_history(ticker, length):
   interval = getInterval(length)
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/chart/{interval}?token={os.getenv("iexToken")}'
   
   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   if (rawResponse.status_code != 200):
      rawResponse.raise_for_status()

   response = rawResponse.json()

   data = formatData(response, interval)

   if length == 'recent':
      data = [data[-1]]
   
   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return data

def getSharePrice(ticker):
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/quote?token={os.getenv("iexToken")}'
   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   if (rawResponse.status_code != 200):
      rawResponse.raise_for_status()

   response = rawResponse.json()

   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return response["latestPrice"]

# Returns a dictionary of stocks and their prices
def getSharePrices(tickers):
   tickersDelimited = ','.join(tickers)
   requestUrl = f'https://cloud.iexapis.com/stable/stock/market/quote?symbols={tickersDelimited}&token={os.getenv("iexToken")}&filter=symbol,latestPrice'
   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   if (rawResponse.status_code != 200):
      rawResponse.raise_for_status()

   response = rawResponse.json()

   # Converting to dictionary because it is better
   priceDict = {}
   for stock in response:
      priceDict[stock['symbol']] = stock['latestPrice']

   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return priceDict

def getInterval(length):
   if length == 'week':
      return WEEK
   elif length == 'month':
      return MONTH
   elif length == 'year':
      return YEAR


def formatData(jsonData, interval):
   data = [] 
   for item in jsonData:

      itemDateTime = formatDateTime(item, interval)
      data.append({
         'time' : itemDateTime.strftime(DATETIME_FORMAT),
         'epochTime' : itemDateTime.timestamp(),
         'price' : item['close']
      })

   data.sort(key=lambda item:item['epochTime'], reverse=False)
   return data

# Returns a string
def formatDateTime(data, interval):
   return datetime.strptime(data['date'], IEX_DATE_FORMAT)

# Expects a requests.HTTPError object
def handleIexError(error):
   if error.response.status_code == 401:
      return make_response(jsonify(InvalidIexToken=errors['invalidIexToken']), 401)
   elif error.response.status_code == 404:
      return make_response(jsonify(UnsupportedTicker=errors['unsupportedTicker']), 400)
   else:
      return make_response(jsonify(IexUnavailable=errors['iexUnavailable']), 503)
