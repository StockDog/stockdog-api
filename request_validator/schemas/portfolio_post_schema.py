from ..field import Field
from .util_schema import validateName, validateBuyPower

fields = [
   Field('name', str, True, validateName),
   Field('buyPower', int, False, validateBuyPower),
   Field('inviteCode', str, False)
]

