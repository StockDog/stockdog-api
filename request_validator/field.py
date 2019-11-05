class Field:
   def __init__(self, name, datatype, isRequired, customValidate=None):
      self.name = name
      self.datatype = datatype
      self.isRequired = isRequired
      self.customValidate = customValidate

