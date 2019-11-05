from flask import g, jsonify, make_response, request, Response
from functools import update_wrapper, wraps

from util.error_map import errors


def login_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
      try:
         validate_session()
      except Exception as e:
         return make_response(jsonify(NotLoggedIn=errors['notLoggedIn']), 401)

      return f(*args, **kwargs)
   return decorator


def validate_session():
   authHeader = request.headers.get('Authorization').split(' ')
   if len(authHeader) != 2 or authHeader[0] != "token":
      raise Exception('Invalid token')
   authToken = authHeader[1]
   g.cursor.execute("SELECT * FROM User WHERE token = %s", authToken)
   g.user = g.cursor.fetchone()
   if g.user is None:
      raise Exception('Invalid token')


def session_belongsTo_user(userId):
   return g.user['id'] == int(userId)


def portfolio_belongsTo_user(portfolioId):
   g.cursor.execute("SELECT userId FROM Portfolio WHERE id = %s", portfolioId)
   portfolio = g.cursor.fetchone()
   return False if not portfolio else portfolio.get('userId', -1) == g.user['id'] 