from ..field import Field
from .util_schema import validateName, validateEmail, validatePassword


fields = [
   Field('firstName', str, True, validateName),
   Field('lastName', str, True, validateName),
   Field('email', str, True, validateEmail),
   Field('password', str, True, validatePassword)
]