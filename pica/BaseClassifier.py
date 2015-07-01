"""
Base class for all classifiers.

@author: Norman MacDonald
"""

from io.BaseParameterIO import BaseParameterIO
		
class BaseClassifier:
	"""Base class for all classifiers."""
	def load_parameters(self,parameters_filename=None):
		if parameters_filename == None:
			return {}
		parameter_io = BaseParameterIO()
		return parameter_io.load(parameters_filename)
		
	
	def __init__(self,parameters_filename,model_filename,model_accuracy):
		self.null_flag = "NULL"
		
		pass
	
	def set_null_flag(self,null_flag):
		"""Set the flag to represent null."""
		self.null_flag = null_flag
		
	def test(self,sample_set,target_class):
		"""Test a model on a sample set."""
		pass
		
	def classify(self,model,sample):
		"""Test a model on a single sample."""
		pass
	
