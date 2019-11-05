from pprint import pprint

class Colors:
   HEADER = '\033[95m'
   OKBLUE = '\033[94m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'

   RESTORE='\033[0m'
   RED='\033[00;31m'
   GREEN='\033[00;32m'
   YELLOW='\033[00;33m'
   BLUE='\033[00;34m'
   CYAN='\033[00;36m'

class Logger:

   def __init__(self, isActive=True, isVerbose=True, isDebug=True):
      self.isActive = isActive
      self.isVerbose = isVerbose
      self.isDebug = isDebug

   def info(self, msg, isPprint=False):
      if self.isActive:
         if isPprint:
            print (Colors.CYAN + "[INFO]" + Colors.RESTORE)
            pprint (msg)
         else:
            print (Colors.CYAN + "\t[INFO] : " + msg + Colors.RESTORE)

   def debug(self, msg, isPprint=False):
      if self.isActive and self.isDebug:
         if isPprint:
            print (Colors.HEADER + "[DEBUG]" + Colors.RESTORE)
            pprint(msg)
         else:
            print (Colors.HEADER + "\t[DEBUG] : " + msg + Colors.RESTORE)

   def warn(self, msg, isPprint=False):
      if self.isActive:
         if isPprint:
            print(Colors.WARNING + "[WARN]" + Colors.RESTORE)
            pprint(msg)
         else:
            print(Colors.WARNING + "\t[WARN] : " + msg + Colors.RESTORE)

   def error(self, msg, isPprint=False):
      if self.isActive:
         if isPprint:
            print(Colors.FAIL + "[ERROR]" + Colors.RESTORE)
            pprint(msg)
         else:
            print(Colors.FAIL + "\t[ERROR] : " + msg + Colors.RESTORE)

   def verbose(self, msg, isPprint=False):
      if self.isActive and self.isVerbose:
         if isPprint:
            print(Colors.GREEN + "[VERBOSE]" + Colors.RESTORE)
            pprint(msg)
         else:
            print(Colors.GREEN + "\t[VERBOSE] : " + msg + Colors.RESTORE)


