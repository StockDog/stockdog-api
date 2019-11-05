from ..field import Field
from .util_schema import validateName, validateDate, validateBuyPower

fields = [
   Field('name', str, True, validateName),
   Field('start', str, True, validateDate),
   Field('end', str, True, validateDate),
   Field('startPos', int, False, validateBuyPower)
]