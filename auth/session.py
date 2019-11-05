from flask import Blueprint, request, Response, jsonify, g, make_response

from util.error_map import errors

session_api = Blueprint('session_api', __name__)


@session_api.route('/api/session/validation', methods=['POST'])
def validateSession():
  body = request.get_json()

  g.cursor.execute("SELECT token FROM User WHERE id = %s", body['userId'])
  row = g.cursor.fetchone()

  if row is None:
    return make_response(jsonify(error=errors['nonexistentUser']), 404)
  
  else:
      if row['token'] == body['token']:
        return Response(status=200)
      else:
        return Response(status=401)
