from ..field import Field
from .util_schema import validateName, validateBuyPower, validatePosInt

fields = [
    Field('portfolioId', int, True, validatePosInt),
    Field('ticker', str, True)
]