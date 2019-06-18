from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, Response, g
import requests
import simplejson as json
import time

from auth import auth
from request_validator import validator
from request_validator.schemas import charts_schema
from util.error_map import errors

DAY = '1d'
MONTH = '1m'
YEAR = '1y'

IEX_DATETIME_FORMAT = '%Y%m%d %H:%M'
IEX_DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

stock_api = Blueprint('stock_api', __name__)

IEX_URL_PREFIX = 'https://api.iextrading.com/1.0/stock/'

@stock_api.route('/api/v1.0/stock/<ticker>', methods=['GET'])
@auth.login_required
def getStock(ticker):
	stockInformation = getStockInformation(ticker)

	if (stockInformation == None):
		return make_response(jsonify(InvalidTicker=errors['unsupportedTicker']), 400)

	return json.dumps(stockInformation)

def getStockInformation(ticker):
	requestUrl = IEX_URL_PREFIX + ticker + '/company'

	g.log.info('IEX API hitting: ' + requestUrl)
	startTime = time.time()
	rawResponse = requests.get(requestUrl)
	iexTime = time.time() - startTime

	try:
		response = rawResponse.json()
	except:
		return None

	parseTime = time.time() - startTime
	g.log.info('IEX time is: ' + str(iexTime))
	g.log.info('Parsing data time is: ' + str(parseTime))

	return response

@stock_api.route('/api/v1.0/stock/<ticker>/chart', methods=['GET'])
# @auth.login_required
@validator.validate_params(charts_schema.fields)
def extract_args(ticker):
   length = request.args.get('length')

   return get_history(ticker, length)


def get_history(ticker, length):
   interval = getInterval(length)
   requestUrl = IEX_URL_PREFIX + ticker + '/chart/' + interval + '?token=pk_5ab485c89b3841b0994702a5fdfcf862'
   
   g.log.info('IEX API hitting: ' + requestUrl)
   startTime = time.time()
   rawResponse = requests.get(requestUrl)
   iexTime = time.time() - startTime

   try:
      response = rawResponse.json()
   except:
      return make_response(jsonify(InvalidTicker=errors['unsupportedTicker']), 400)

   data = formatData(response, interval)
   if len(data) == 0:
      return make_response(jsonify(IEXUnavailable=errors['iexUnavailable']), 500)
   
   if length == 'recent':
      data = [data[-1]]
   
   parseTime = time.time() - startTime
   g.log.info('IEX time is: ' + str(iexTime))
   g.log.info('Parsing data time is: ' + str(parseTime))

   return json.dumps(data)


def getSharePrice(ticker):
   return json.loads(get_history(ticker, 'recent'))[0]['price']


def getInterval(length):
   if length == 'recent' or length == 'day':
      return DAY
   elif length == 'week' or length == 'month':
      return MONTH
   elif length == 'year':
      return YEAR


def formatData(jsonData, interval):
   if interval == DAY:
      return formatDataIntraday(jsonData)
   elif interval == MONTH or interval == YEAR:
      return formatDataInterDay(jsonData)

   
def formatDataInterDay(jsonData):
   data = []
   for item in jsonData:

      itemTime = datetime.strptime(item['date'], IEX_DATE_FORMAT)
      data.append({
         'time' : itemTime.strftime(DATETIME_FORMAT),
         'epochTime' : itemTime.timestamp(),
         'price' : item['open']
      })

   data.sort(key=lambda item:item['epochTime'], reverse=False)
   return data


def formatDataIntraday(jsonData):
   data = [] 
   for item in jsonData:
      if item['average'] < 0:
         continue

      itemTime = datetime.strptime(item['date'] + ' ' + item['minute'], IEX_DATETIME_FORMAT)
      data.append({
         'time' : itemTime.strftime(DATETIME_FORMAT),
         'epochTime' : itemTime.timestamp(),
         'price' : item['average']
      })

   data.sort(key=lambda item:item['epochTime'], reverse=False)
   return data
