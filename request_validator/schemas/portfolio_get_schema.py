from ..field import Field
from .util_schema import validatePosInt

fields = [
   Field('leagueId', int, False, validatePosInt)
]