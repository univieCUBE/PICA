"""Base loader for parameter files.  Converts param=value to struct.param"""

class BaseParameterIO:
	def __init__(self):
		pass
	def load(self,filename):
		parameters = {}
		lines = open(filename).readlines()
		print lines
		for line in lines:
			if not line.strip().startswith("#"):
				param,value = [x.strip() for x in line.split("#")[0].split("=")]
				parameters[param] = value
		return parameters
	