from enum import Enum

from ..field import Field
from .util_schema import validateEmail

fields = [
   Field('email', str, True, validateEmail),
   Field('password', str, True)
]

fields_google = [
   Field('googleIdToken', str, True),
   Field('appType', str, True), # Needs to be either expo or standalone
   Field('os', str, True) # Needs to be either ios or android
]

fields_apple = [
   Field('appleIdToken', str, True),
   Field('appType', str, True),
   Field('givenName', str, False),
   Field('familyName', str, False)
]