from flask import Blueprint, request, Response, g, jsonify, make_response
import simplejson as json
from datetime import datetime

from auth import auth
import routes.portfolio as portfolio_funcs
from request_validator import validator
from request_validator.schemas import league_post_schema
from util.utility import Utility
from util.error_map import errors

league_api = Blueprint('league_api', __name__)

DATE_FORMAT = "%m-%d-%Y"
DAYS_IN_YEAR = 365
DEFAULT_START_POS = 10000


@league_api.route('/api/v1.0/leagues', methods=['POST'])
@auth.login_required
@validator.validate_body(league_post_schema.fields)
def post_league():
    body = request.get_json()
    start_date = datetime.strptime(body['start'], DATE_FORMAT)
    end_date = datetime.strptime(body['end'], DATE_FORMAT)
    if start_date > end_date:
        return make_response(jsonify(EndBeforeStart=errors['endBeforeStart']), 400)

    league_duration = (end_date - start_date).days
    if league_duration > DAYS_IN_YEAR:
        return make_response(jsonify(LeagueDurationTooLong=errors['leagueDurationTooLong']), 400)

    start_pos = body.get('startPos') or DEFAULT_START_POS
    invite_code = Utility.getInviteCode()

    g.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
                     "VALUES (%s, %s, %s, %s, %s, %s)",
                     [body['name'], start_date, end_date, start_pos, invite_code, g.user['id']])

    return jsonify(inviteCode=invite_code, id=g.cursor.lastrowid, startPos=start_pos)


@league_api.route('/api/v1.0/leagues/<league_id>', methods=['GET'])
@auth.login_required
def get_league(league_id):
    g.cursor.execute("SELECT * FROM League WHERE id=%s", league_id)
    league_info = g.cursor.fetchone()

    # no league found
    if not league_info:
        return make_response(jsonify(error='leagueNotFound', message=errors['leagueNotFound']), 404)

    # get associated portfolios
    g.cursor.execute("SELECT * FROM Portfolio WHERE leagueId=%s", league_id)
    portfolios = g.cursor.fetchall()

    # attach portfolio value for each portfolio
    for portfolio in portfolios:
        portfolio_funcs.attach_portfolioItems(portfolio)
        portfolio_funcs.attach_portfolio_value(portfolio)

    return jsonify(
        id=league_info["id"],
        name=league_info["name"],
        startPos=league_info["startPos"],
        start=league_info["start"],
        end=league_info["end"],
        portfolios=portfolios
    )


@league_api.route('/api/v1.0/leagues', methods=['GET'])
@auth.login_required
def get_leagues():
    g.cursor.execute('SELECT id, name, startPos, start, end, inviteCode FROM League')
    leagues = g.cursor.fetchall()

    # Attach league status
    # Stringfy dates
    for league in leagues:
        league['status'] = get_league_status(league['start'], league['end'])
        league['start'] = league['start'].strftime('%m-%d-%Y')
        league['end'] = league['end'].strftime('%m-%d-%Y')

    return json.dumps(leagues)


def get_league_status(start, end):
    if start < datetime.now() < end:
        return "active"
    elif end < datetime.now():
        return "ended"
    else:
        return "planned"
