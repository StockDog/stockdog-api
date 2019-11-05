from ..field import Field
from .util_schema import validateLength

fields = [
   Field('length', str, True, validateLength)
]

