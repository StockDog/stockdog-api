from datetime import datetime
from flask import Blueprint, request, Response, g, jsonify, make_response
import simplejson as json

from routes import stock
from auth import auth
from request_validator import validator
from request_validator.schemas import portfolio_post_schema, portfolio_get_schema
from util.utility import Utility
from util.error_map import errors

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

    for portfolio in portfolios:
        attach_portfolioItems(portfolio)
        attach_portfolio_value(portfolio)
        attach_league(portfolio)

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

    attach_portfolioItems(portfolio)
    attach_portfolio_value(portfolio)
    attach_league(portfolio)

    return json.dumps(portfolio)


@portfolio_api.route('/api/v1.0/portfolios/<portfolio_id>/history/<time_frame>', methods=['GET'])
def get_portfolio_history(portfolio_id, time_frame):
    if not time_frame == 'month' or 'year' or 'all':
        return make_response(jsonify(error='invalidTimeFrame', message=errors['invalidTimeFrame']), 404)

    if time_frame == 'all':
        return json.dumps(get_all_portfolio_history(portfolio_id))
    elif time_frame == 'year':
        return json.dumps(get_year_portfolio_history(portfolio_id))
    else:
        return json.dumps(get_month_portfolio_history(portfolio_id))


def get_all_portfolio_history(portfolio_id):
    g.cursor.execute('SELECT * FROM PortfolioHistory WHERE portfolioId = %s', portfolio_id)
    history = g.cursor.fetchall()

    if len(history) == 0:
        return None

    return history


def get_year_portfolio_history(portfolio_id):
    history = get_all_portfolio_history(portfolio_id)
    year_history = []

    if len(history) == 0:
        return None

    # Gather every tenth data point
    history_data_idx = 0
    while history[history_data_idx]:
        # Prepend data point
        year_history = history[history_data_idx] + year_history
        history_data_idx = history_data_idx + 10

    return year_history

def get_month_portfolio_history(portfolio_id):
    history = get_all_portfolio_history(portfolio_id)

    if len(history) == 0:
        return None

    # Get the last 20 endpoints
    return history[max(1, len(history) - 20)]


def attach_portfolioItems(portfolio):
    items = []
    g.cursor.execute("SELECT id, shareCount, avgCost, ticker FROM PortfolioItem WHERE portfolioId = %s",
                     portfolio['id'])
    items = g.cursor.fetchall()

    for item in items:
        item['price'] = stock.getSharePrice(item['ticker'])
        item['companyName'] = stock.getStockInformation(item['ticker'])['companyName']

        # Calculating gain.
        currentTotal = float(item['price']) * float(item['shareCount'])
        purchasedTotal = float(item['avgCost']) * float(item['shareCount'])
        item['gain'] = currentTotal - purchasedTotal

    portfolio['items'] = items


def attach_portfolio_value(portfolio):
    value = float(portfolio['buyPower'])
    for item in portfolio['items']:
        value += float(stock.getSharePrice(item['ticker'])) * item['shareCount']

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

# @portfolio_api.route('/api/portfolio/<portfolioId>', methods=['GET'])
# def get_portfolio(portfolioId):
#    g.cursor.execute("SELECT p.id AS id, ticker, shareCount, avgCost, name, buyPower, leagueId " +
#       "FROM Portfolio AS p LEFT JOIN PortfolioItem as pi ON p.id = pi.portfolioId " + 
#       "WHERE p.id = %s", portfolioId)

#    portfolio = g.cursor.fetchall()
#    portfolioWithValues = add_portfolio_values(portfolio)
#    return json.dumps(portfolioWithValues)


# @portfolio_api.route('/api/portfolio/<portfolioId>/value', methods=['GET'])
# def get_portfolio_value(portfolioId):
#    portfolioItems = json.loads(get_portfolio(portfolioId))
#    value = 0
#    for item in portfolioItems:
#       if item['ticker'] is not None:
#          value += float(json.loads(stock.get_history(item['ticker'], 'now'))['price']) * item['shareCount']

#    return json.dumps({"value": value + float(portfolioItems[0]['buyPower'])})


# @portfolio_api.route('/api/portfolio/<portfolioId>/history', methods=['POST'])
# def post_portfolio_history(portfolioId):
#    body = request.get_json()
#    try:
#       result = PortfolioHistorySchema().load(body)
#    except ValidationError as err:
#       return make_response(json.dumps(err.messages), 400)

#    now = datetime.now()

#    g.cursor.execute("INSERT INTO PortfolioHistory(portfolioId, datetime, value) VALUES (%s, %s, %s)",
#       [portfolioId, str(now), body['value']])

#    return Response(status=200)


# @portfolio_api.route('/api/portfolio/<portfolioId>/history', methods=['GET'])
# def get_portfolio_history(portfolioId):

#    g.cursor.execute("SELECT value, datetime FROM Portfolio AS p JOIN PortfolioHistory AS ph ON p.id = ph.portfolioId " +
#       "WHERE portfolioId = %s", portfolioId)

#    portfolio = g.cursor.fetchall()
#    return json.dumps(portfolio, default=str)
