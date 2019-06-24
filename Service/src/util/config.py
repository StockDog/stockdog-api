import simplejson as json

CONFIG_FILE_PATH = 'Service/src/config.json'
ROOT_FOLDER_NAME = 'stockdog-api/'

__config = None

def getConfig():
   # Variable is only global in the module
   global __config
   if (__config is None):
      __config = __importConfig()
   return __config

def __importConfig():
   configFile = open(__getConfigFilePath(), 'r')
   config = json.load(configFile)
   configFile.close()

   return config

def __getConfigFilePath():
   try:
      return './config.json'
      cwd = os.getcwd()		
      strIdx = cwd.find(ROOT_FOLDER_NAME)		
      return cwd[:strIdx + len(ROOT_FOLDER_NAME)] + CONFIG_FILE_PATH
   except Exception as e:
      raise Exception('The config filename was not provided or poorly formatted') 