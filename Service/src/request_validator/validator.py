from flask import g, make_response, jsonify, request
from functools import update_wrapper, wraps
import simplejson as json

from .validation_error import ValidationError
from util.error_map import errors

def validate(data, fields):
   errors = []
   check_headers(errors)
   if (len(errors) > 0):
      raise ValidationError(errors)

   check_required_fields(data, fields, errors)
   if (len(errors) > 0):
      raise ValidationError(errors)

   check_field_validity(data, fields, errors)
   if (len(errors) > 0):
      raise ValidationError(errors)

   return None


def check_headers(errors):

   contentTypeHeader = request.headers.get('Content-Type')
   if request.method != 'GET' and contentTypeHeader is None:
      errors.append({'MissingHeader' : 'Content-Type is a required header'})
   elif request.method != 'GET' and contentTypeHeader and contentTypeHeader != 'application/json':
      errors.append({'InvalidHeader' : 'API only accepts Content-Type of application/json'})
   
   return errors


def check_required_fields(data, fields, errors):
   for field in fields:
      if field.isRequired and data.get(field.name) is None:
         errors.append({'MissingField' : field.name + ' is a required field'})
      
   return errors


def check_field_validity(data, fields, errors):
   for field in fields:
      if not field.isRequired and data.get(field.name) is None:
         pass
      elif field.customValidate is not None:
         field.customValidate(data.get(field.name), field, errors)
      elif field.datatype == str and data.get(field.name) is not None:
         validate_str(data.get(field.name), field, errors)
      elif field.datatype == int and data.get(field.name) is not None:
         validate_int(data.get(field.name), field, errors)
      else:
         g.log.error("Unexpected datatype encountered in request validation for " + field.name)
   
   return errors


def validate_str(datum, field, errors):
   if type(datum) != str:
      errors.append({'InvalidField' : field.name + ' is not a string or formatted incorrectly'})
   
   return errors


def validate_int(datum, field, errors):
   if type(datum) != int:
      errors.append({'InvalidField' : field.name + ' is not an int or formatted incorrecly'})
   
   return errors


def login_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
      try: 
         validate_session()
      except Exception as e:
         return make_response(jsonify(NotLoggedIn=errors['notLoggedIn']),401)
      
      return f(*args, **kwargs)
   return decorator


def validate_headers(f):
   @wraps(f)
   def decorator(*args, **kwargs):
      try:
         errors = []
         # This function check if content-type is application/json no matter what the request it
         # This does not make sense because get calls with no body do not have content
         # axios calls in the front end do not like this code law
         # check_headers(errors)
         if (len(errors) > 0):
            raise ValidationError(errors)
      
      except ValidationError as e:
         return make_response(json.dumps(e.errors), 400)
      
      return f(*args, **kwargs)
   return decorator


def validate_params(fields):
   def decorator(fn):
      def wrap(*args, **kwargs):
         try:
            validate(request.args, fields)
         except ValidationError as e:
            g.log.error(json.dumps(e.errors))
            return make_response(json.dumps(e.errors), 400)
         
         return fn(*args, **kwargs)
      return update_wrapper(wrap, fn)
   return decorator


def validate_body(fields):
   def decorator(fn):
      def wrap(*args, **kwargs):
         try:
            validate(request.get_json(), fields)
         except ValidationError as e:
            g.log.error(json.dumps(e.errors));
            return make_response(json.dumps(e.errors), 400)
         
         return fn(*args, **kwargs)
      return update_wrapper(wrap, fn)
   return decorator