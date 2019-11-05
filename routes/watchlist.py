import requests
from flask import Blueprint, jsonify, make_response, request, Response, g
import simplejson as json

from auth import auth
from request_validator import validator
from request_validator.schemas import watchlist_post_del_schema
from routes.stock import getSharePrice, handleIexError, getSharePrices
from util.error_map import errors

watchlist_api = Blueprint('watchlist_api', __name__)


@watchlist_api.route('/api/v1.0/watchlists', methods=['POST'])
@auth.login_required
@validator.validate_body(watchlist_post_del_schema.fields)
def post_watchlist():
    body = request.get_json()

    error = validate_post_del_watchlist(body)

    if error:
        return error

    # Make sure ticker doesn't exist in portfolio already
    g.cursor.execute('SELECT id FROM Watchlist WHERE portfolioId = %s AND ticker = %s',
                     [body['portfolioId'], body['ticker']])

    if g.cursor.rowcount > 0:
        return make_response(jsonify(error=errors['tickerAlreadyInWatchlist']), 400)

    # Insert into table
    g.cursor.execute('INSERT INTO Watchlist(portfolioId, ticker) VALUES (%s, %s)',
                     [body['portfolioId'], body['ticker']])

    return jsonify(id=g.cursor.lastrowid)


@watchlist_api.route('/api/v1.0/watchlists', methods=['DELETE'])
@auth.login_required
@validator.validate_body(watchlist_post_del_schema.fields)
def del_watchlist():
    body = request.get_json()

    error = validate_post_del_watchlist(body)

    if error:
        return error

    # Insert into table
    g.cursor.execute('DELETE FROM Watchlist WHERE portfolioId = %s AND ticker = %s',
                     [body['portfolioId'], body['ticker']])

    if g.cursor.rowcount == 1:
        return jsonify(success=True)
    else:
        return make_response(jsonify(error=errors['tickerNotWatchlisted']), 400)


# Used to validate both post and del endpoints for watchlists
def validate_post_del_watchlist(body):
    # See if user belongs to given portfolioId
    if not auth.portfolio_belongsTo_user(body['portfolioId']):
        return Response(status=403)

    # See if the ticker is valid
    try:
        getSharePrice(body['ticker'])
    except requests.HTTPError as e:
        return handleIexError(e)
    except TypeError:
        return make_response(jsonify(error=errors['unsupportedTicker']), 400)

@watchlist_api.route('/api/v1.0/watchlists/<portfolio_id>', methods=['GET'])
@auth.login_required
def get_watchlist(portfolio_id):
    # Make sure the user belongs to the portfolio
    if not auth.portfolio_belongsTo_user(portfolio_id):
        return Response(status=403)

    g.cursor.execute('SELECT * FROM Watchlist WHERE portfolioId = %s', [portfolio_id])
    watchlist = g.cursor.fetchall()

    # Get all the watchlist ticker values
    tickers = []
    for item in watchlist:
        tickers.append(item['ticker'])

    tickerPrices = getSharePrices(tickers)

    for item in watchlist:
        item['price'] = tickerPrices[item['ticker']]

    return jsonify(watchlist)