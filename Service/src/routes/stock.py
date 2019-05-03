import requests
from flask import g, Blueprint, make_response, jsonify
import time
import simplejson as json

from request_validator import validator
from auth import auth
from util.error_map import errors

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
