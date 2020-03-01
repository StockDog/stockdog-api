from datetime import datetime
from flask import Blueprint, request, Response, g, jsonify, make_response
import simplejson as json

from routes import stock
from auth import auth
from request_validator import validator
from request_validator.schemas import portfolio_post_schema, portfolio_get_schema
from util.utility import Utility
from util.error_map import errors
from clients.elastic_search_client import get_stocks_info

portfolio_api = Blueprint('portfolio_api', __name__)

DEFAULT_BUYPOWER = 10000


@portfolio_api.route('/api/v1.0/portfolios', methods=['POST'])
@auth.login_required
@validator.validate_body(portfolio_post_schema.fields)
def post_portfolio():
    body = request.get_json()
    buyPower = body.get('buyPower') or DEFAULT_BUYPOWER

    if 'inviteCode' in body:
        g.cursor.execute("SELECT id, name, startPos FROM League WHERE inviteCode = %s", body['inviteCode'])
        league = g.cursor.fetchone()

        if league is None:
            return make_response(jsonify(InviteCodeMismatch=errors['inviteCodeMismatch']), 400)

        g.cursor.execute("INSERT INTO Portfolio(name, buyPower, userId, leagueId) VALUES (%s, %s, %s, %s)",
                         [body['name'], league['startPos'], g.user['id'], league['id']])

        portfolio_id = g.cursor.lastrowid

        # Add initial portfolio history point
        g.cursor.execute("INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES (%s, NOW(), %s)",
                         [portfolio_id, league['startPos']])

        return jsonify(id=g.cursor.lastrowid, buyPower=league['startPos'], leagueId=league['id'],
                       leagueName=league['name'])

    else:
        g.cursor.execute("INSERT INTO Portfolio(name, buyPower, userId) VALUES (%s, %s, %s)",
                         [body['name'], buyPower, g.user['id']])

        return jsonify(id=g.cursor.lastrowid, buyPower=buyPower)


@portfolio_api.route('/api/v1.0/portfolios', methods=['GET'])
@auth.login_required
@validator.validate_params(portfolio_get_schema.fields)
def get_portfolios():
    g.cursor.execute("SELECT id, buyPower, name, userId, leagueId FROM Portfolio " +
                     "WHERE userId = %s", g.user['id'])

    portfolios = g.cursor.fetchall()

    attach_portfolioItems(portfolios)
    for portfolio in portfolios:
        attach_portfolio_value(portfolio)
        attach_league(portfolio)
        attach_portfolio_history(portfolio)

    return json.dumps(portfolios)


@portfolio_api.route('/api/v1.0/portfolios/<portfolioId>', methods=['GET'])
@auth.login_required
@validator.validate_headers
def get_portfolio(portfolioId):
    if not auth.portfolio_belongsTo_user(portfolioId):
        return Response(status=403)

    g.cursor.execute("SELECT id, buyPower, name, userId, leagueId FROM Portfolio " +
                     "WHERE id = %s", portfolioId)

    portfolio = g.cursor.fetchone()
    if portfolio is None:
        return Response(status=404)

    attach_portfolioItems([portfolio])
    attach_portfolio_value(portfolio)
    attach_league(portfolio)
    attach_portfolio_history(portfolio)


    return json.dumps(portfolio)

# Pass in array of portfolios
def attach_portfolioItems(portfolios):
    portfolioIds = "" # SQL array
    tickers = []
    items = []

    # Don't do anything if there is no portfolios
    if len(portfolios) == 0:
        return;

    # Trying to get "1, 2, 3"
    for portfolio in portfolios:
        if portfolioIds == "":
            portfolioIds = f"{portfolio['id']}"
        else:
            portfolioIds = portfolioIds + f", {portfolio['id']}"

        # Also start portfolio[items] with an empty array
        portfolio['items'] = []

    g.cursor.execute(f'SELECT id, shareCount, avgCost, ticker, portfolioId FROM PortfolioItem WHERE portfolioId IN ({portfolioIds})')
    items = g.cursor.fetchall()

    for item in items:
        tickers.append(item['ticker'])

    # Remove duplicate tickers
    tickers = list(dict.fromkeys(tickers))

    # Only get prices and infos if tickers isn't empty
    if (len(tickers) > 0):
        prices = stock.getSharePrices(tickers)
        infos = get_stocks_info(tickers)

    for item in items:
        item['price'] = prices[item['ticker']]
        item['companyName'] = infos[item['ticker']]['Name']

        # Calculating gain.
        currentTotal = float(item['price']) * float(item['shareCount'])
        purchasedTotal = float(item['avgCost']) * float(item['shareCount'])
        item['gain'] = currentTotal - purchasedTotal

    for portfolio in portfolios:
        for item in items:
            if item['portfolioId'] == portfolio['id']:
                portfolio['items'].append(item)
                

def attach_portfolio_value(portfolio):
    value = float(portfolio['buyPower'])
    for item in portfolio['items']:
        value += float(item['price']) * item['shareCount']

    portfolio['value'] = value


def attach_league(portfolio):
    g.cursor.execute("SELECT id, name, startPos, start, end FROM League WHERE id=%s", portfolio['leagueId'])
    league_info = g.cursor.fetchone()

    # no league found
    if not league_info:
        portfolio['league'] = None
    else:
        portfolio['league'] = league_info

    del portfolio['leagueId']

    # Stringify dates
    portfolio['league']['start'] = portfolio['league']['start'].strftime('%m-%d-%Y')
    portfolio['league']['end'] = portfolio['league']['end'].strftime('%m-%d-%Y')


def attach_portfolio_history(portfolio):
    g.cursor.execute("SELECT id, portfolioId, datetime, value FROM PortfolioHistory WHERE portfolioId=%s",
        (portfolio['id']))
    portfolio_history = g.cursor.fetchall()

    # Stringify dates
    for item in portfolio_history:
        item['datetime'] = item['datetime'].strftime('%m-%d-%Y')

    portfolio['history'] = portfolio_history