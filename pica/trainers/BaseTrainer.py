"""
Base class for all classification training algorithms.

@author: Norman MacDonald
@date: 2010-02-16
"""

from pica.io.BaseParameterIO import BaseParameterIO
class BaseTrainer():
	"""Base class for all classification training algorithms."""
	def __init__(self,parameters):
		"""Initialize a new trainer."""
		self.null_flag = "NULL"
	
	def remap_index_to_feature(self,model,sample_set):
		return model
		
	def remap_feature_to_index(self,model,sample_set):
		return model
	
	def load_parameters(self,parameters_filename=None):
		if parameters_filename == None:
			return {}
		parameter_io = BaseParameterIO()
		return parameter_io.load(parameters_filename)
		
	
	def set_null_flag(self,flag_value):
		"""Set the flag to represent null."""
		self.null_flag = flag_value
		
	def train(self,samples):
		"""Return a model constructed from training on samples."""
		pass
