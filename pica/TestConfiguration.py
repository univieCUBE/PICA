"""
Stores a testing configuration for crossvalidation.  
A test consists of an optional feature selection step, a training step, and a classification step.
Each test configuration is run on the same samples in the same crossvalidated fold to allow for
paired comparisons of performance.
"""
class TestConfiguration:
	def __init__(self,name,feature_selector=None,trainer=None,classifier=None):
		self.name = name
		self.feature_selector = feature_selector
		self.trainer = trainer
		self.classifier = classifier
		