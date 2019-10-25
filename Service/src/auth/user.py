from flask import Blueprint, request, Response, g, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import simplejson as json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from auth import auth
from request_validator import validator
from request_validator.schemas import user_schema, login_schema
from .token_manager import getUniqueToken
from util.error_map import errors
from util.config import getConfig

user_api = Blueprint('user_api', __name__)

@user_api.route('/api/v1.0/users', methods=['POST'])
@validator.validate_body(user_schema.fields)
def post_user():
   body = request.get_json()

   g.cursor.execute("SELECT * FROM User WHERE email = %s", body['email'])
   sameEmailusers = g.cursor.fetchall()
   if len(sameEmailusers) > 0:
      return make_response(jsonify(DuplicateEmail=errors['duplicateEmail']), 400)

   passwordHash = generate_password_hash(body['password'])

   g.cursor.execute("INSERT INTO User(firstName, lastName, email, password, type) VALUES (%s, %s, %s, %s, %s)",
      (body['firstName'], body['lastName'], body['email'], passwordHash, "none"))
   
   return jsonify(id=g.cursor.lastrowid)


@user_api.route('/api/v1.0/users/session', methods=['POST'])
@validator.validate_body(login_schema.fields)
def login_user():
   body = request.get_json()

   g.cursor.execute("SELECT * FROM User WHERE email = %s", body['email'])
   user = g.cursor.fetchone()

   if user:
      if user['token']:
         return jsonify(userId=user['id'], token=user['token'])

      passHash = user['password']
      if check_password_hash(passHash, body['password']):
         token = getUniqueToken()
         g.cursor.execute("UPDATE User SET token = %s WHERE id = %s", [token, user['id']])
         return jsonify(userId=user['id'], token=token)

      else:
         return make_response(jsonify(PasswordMismatch=errors['passwordMismatch']), 401)
   
   else:
      return make_response(jsonify(NonexistentUser=errors['nonexistentUser']), 401)


@user_api.route('/api/v1.0/users/session/google', methods=['POST'])
@validator.validate_body(login_schema.fields_google)
def login_user_google():
   body = request.get_json()

   # Validate the token is from Google
   if body['appType'] == "expo" and body['os'] == "ios":
      clientId = getConfig()['auth']['google']['authClientIdExpoIos']
   elif body['appType'] == "standalone" and body['os'] == "ios":
      clientId = getConfig()['auth']['google']['authClientIdStandaloneIos']
   elif body['appType'] == "expo" and body['os'] == "android":
      clientId = getConfig()['authClientIdExpoAndroid']
   elif body['appType'] == "standalone" and body['os'] == "android":
      clientId = getConfig()['auth']['google']['authClientIdStandaloneAndroid']
   else:
      make_response(jsonify(error='invalidAppTypeOrOs', message=errors['invalidAppTypeOrOs']), 400)

   idinfo = id_token.verify_oauth2_token(body['googleIdToken'], google_requests.Request(), clientId)

   if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        make_response(jsonify(error='wrongIssuerGoogle', message=errors['wrongIssuerGoogle']), 400)

   # All checks passed, check to see if this user has logged in before
   sub = idinfo['sub']

   g.cursor.execute("SELECT * FROM User WHERE sub = %s", sub)
   user = g.cursor.fetchone()

   # If first time user logging in, create row
   if not user:
      g.cursor.execute("INSERT INTO User(firstName, lastName, email, sub, type) VALUES (%s, %s, %s, %s, %s)",
      (idinfo['given_name'], idinfo['family_name'], idinfo['email'], sub, "google"))

      # Get the newly inserted user
      g.cursor.execute("SELECT * FROM User WHERE id = %s", g.cursor.lastrowid)
      user = g.cursor.fetchone()

   if user['token']:
      return jsonify(userId=user['id'], token=user['token'])

   token = getUniqueToken()
   g.cursor.execute("UPDATE User SET token = %s WHERE id = %s", [token, user['id']])
   return jsonify(userId=user['id'], token=token)
   


@user_api.route('/api/v1.0/users/<userId>/session', methods=['DELETE'])
@auth.login_required
@validator.validate_headers
def logout_user(userId):
   if not auth.session_belongsTo_user(userId):
      return Response(status=403)
      
   g.cursor.execute("UPDATE User SET token = NULL WHERE id = %s", userId)

   return Response(status=200)