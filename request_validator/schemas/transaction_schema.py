from ..field import Field
from .util_schema import validatePosInt, validateAction

fields = [
   Field('shareCount', int, True, validatePosInt),
   Field('ticker', str, True),
   Field('action', str, True, validateAction),
   Field('portfolioId', int, True, validatePosInt)
]