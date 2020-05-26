from flask import g, make_response, jsonify, request
from functools import update_wrapper, wraps
import simplejson as json

from .validation_error import ValidationError
from util.error_map import errors

VALID_APP_VERSIONS = ["*", "1.0.6"]

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
    """ Checks to see if there are any errors in the headers

        Parameters
        __________
        errors: array<map>
            Errors array to append to

        Returns
        _______
        array<map>
            New set of errors
    """
    content_type_header = request.headers.get('Content-Type')
    app_version_header = request.headers.get('App-Version')

    if request.method != 'GET':
        content_type_header_error = header_validator('Content-Type', ["application/json"])
        if content_type_header_error != None:
            errors.append(content_type_header_error)

    app_version_header_error = header_validator('App-Version', VALID_APP_VERSIONS)

    if app_version_header_error != None:
        errors.append(app_version_header_error)
    return errors


def header_validator(header_name, values):
    """ Makes sure that the header exists and is one of the values

        Parameters
        __________
        header_name: str
            The name of the header
        values: array<str>
            The possible values for the header

        Returns
        _______
        map
            A map of an error
    """

    header_value = request.headers.get(header_name)

    if header_value is None:
        return {'MissingHeader' : f'{header_name} is a required header'}
    elif header_value not in values:
        return {'InvalidHeader' : f'API only accepts {header_name} of {values}'}


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
         check_headers(errors)
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
