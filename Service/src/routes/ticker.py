from datetime import datetime
from flask import Blueprint, request, Response, g, jsonify, make_response
import simplejson as json

from routes import stock
from auth import auth
from request_validator import validator
from request_validator.schemas import portfolio_post_schema, portfolio_get_schema
from util.utility import Utility
from util.error_map import errors
from services.ticker_service import collectIEXTickersPrice
from services.portfolio_service import calculatePortfolioHistories

ticker_api = Blueprint('ticker_api', __name__)

@ticker_api.route('/api/v1.0/ticker/history', methods=['GET'])
def collectTickerHistory():
    tickers = collectIEXTickersPrice()
    print("Number of tickers collected ",len(tickers))
    return json.loads('{"message":"Collected the ticker prices for today"}')

@ticker_api.route('/api/v1.0/portfolio/history', methods=['GET'])
def collectPortfolioHistory(): 
    calculatePortfolioHistories()
    return json.loads('{"message":"Collected the histories"}')