from datetime import datetime
import random
import string

class Utility:

   def getInviteCode():
      code = random.sample(string.ascii_uppercase + string.digits, 6)
      return ''.join(code)


   def dateToStr(obj):
      if isinstance(obj, datetime):
         return obj.__str__()