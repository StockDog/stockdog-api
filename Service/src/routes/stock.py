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

IEX_URL_PREFIX = 'https://cloud.iexapis.com/v1/stock/'

CONFIG_FILE_PATH = './config.json'

# This needs to be optimized so it doesn't open and close the config file every time.
def getIexToken():
	try:
		configFile = open(CONFIG_FILE_PATH, 'r')
		config = json.load(configFile)
		configFile.close()
		return config['iexToken']
	except Exception as e:
		raise Exception('Could not retrieve the iexToken') 
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
