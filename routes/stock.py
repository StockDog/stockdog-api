from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, Response, g
import requests
import simplejson as json
import time

from auth import auth
from request_validator import validator
from request_validator.schemas import charts_schema
from util.error_map import errors
from util.config import getConfig

DAY = '1d'
MONTH = '1m'
YEAR = '1y'

IEX_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
IEX_DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

stock_api = Blueprint('stock_api', __name__)

IEX_URL_PREFIX = 'https://cloud.iexapis.com/v1/stock/'

# This needs to be optimized so it doesn't open and close the config file every time.
def getIexToken():
   config = getConfig()
   return config['iexToken']

@stock_api.route('/api/v1.0/stocks/<ticker>', methods=['GET'])
@auth.login_required
def getStock(ticker):
   try:
      stockInformation = getStockInformation(ticker)
   except requests.HTTPError as e:
      return handleIexError(e)

   return json.dumps(stockInformation)

def getStockInformation(ticker):
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/company?token={getIexToken()}'

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
   requestUrl = f'https://cloud.iexapis.com/stable/stock/market/company?symbols={tickersDelimited}&token={getIexToken()}'
   
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
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/chart/{interval}?token={getIexToken()}'
   
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
   requestUrl = f'{IEX_URL_PREFIX}{ticker}/quote?token={getIexToken()}'
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
   requestUrl = f'https://cloud.iexapis.com/stable/stock/market/quote?symbols={tickersDelimited}&token={getIexToken()}&filter=symbol,latestPrice'
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
   if length == 'recent' or length == 'day':
      return DAY
   elif length == 'week' or length == 'month':
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

# Handles both intra and inter day data
# Returns a string
def formatDateTime(data, interval):
   if (interval == DAY):
      dateTime = datetime.strptime(data['date'] + ' ' + data['minute'], IEX_DATETIME_FORMAT)
   else:
      dateTime = datetime.strptime(data['date'], IEX_DATE_FORMAT)

   return dateTime

# Expects a requests.HTTPError object
def handleIexError(error):
   if error.response.status_code == 401:
      return make_response(jsonify(InvalidIexToken=errors['invalidIexToken']), 401)
   elif error.response.status_code == 404:
      return make_response(jsonify(UnsupportedTicker=errors['unsupportedTicker']), 400)
   else:
      return make_response(jsonify(IexUnavailable=errors['iexUnavailable']), 503)