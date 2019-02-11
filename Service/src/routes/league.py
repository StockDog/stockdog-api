from flask import Blueprint, request, Response, g, jsonify, make_response
import simplejson as json
from datetime import datetime

from auth import auth
import routes.portfolio as portfolio
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
   startDate = datetime.strptime(body['start'], DATE_FORMAT)
   endDate = datetime.strptime(body['end'], DATE_FORMAT)
   if startDate > endDate:
      return make_response(jsonify(EndBeforeStart=errors['endBeforeStart']), 400)
   
   leagueDuration = (endDate - startDate).days
   if leagueDuration > DAYS_IN_YEAR:
      return make_response(jsonify(LeagueDurationTooLong=errors['leagueDurationTooLong']), 400)

   startPos = body.get('startPos') or DEFAULT_START_POS
   inviteCode = Utility.getInviteCode()

   g.cursor.execute("Insert INTO League(name, start, end, startPos, inviteCode, ownerId) " +
      "VALUES (%s, %s, %s, %s, %s, %s)",
      [body['name'], startDate, endDate, startPos, inviteCode, g.user['id']])

   return jsonify(inviteCode=inviteCode, id=g.cursor.lastrowid, startPos=startPos)
   

@league_api.route('/api/league', methods=['GET'])
def get_leagues():
   inviteCode = request.args.get('inviteCode')

   if inviteCode:
      g.cursor.execute("SELECT * FROM League WHERE inviteCode = %s", inviteCode)
   else:
      g.cursor.execute("SELECT * FROM League")

   leagues = g.cursor.fetchall()
   return json.dumps(leagues, default=Utility.dateToStr)


@league_api.route('/api/league/<leagueId>', methods=['GET'])
def get_league(leagueId):
   g.cursor.execute("SELECT * FROM League WHERE id = %s", leagueId)
   leagueInfo = g.cursor.fetchone()

   if leagueInfo:
      return json.dumps(leagueInfo, default=Utility.dateToStr)
   else:
      return Response(status=404)


@league_api.route('/api/league/<leagueId>/members', methods=['GET'])
def get_league_members(leagueId):
   g.cursor.execute("SELECT p.name, p.id FROM Portfolio AS p JOIN League l ON p.leagueId = l.id " +
      "WHERE l.id = %s", leagueId)

   members = g.cursor.fetchall()
   membersWithPortfolioValue = portfolio.add_portfolio_values(members)

   return json.dumps(membersWithPortfolioValue)
        

    
