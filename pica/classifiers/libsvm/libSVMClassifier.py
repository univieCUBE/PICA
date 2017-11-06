"""
libSVM Classification interface.  The input model must be a LIBSVM model.

LIBSVM is a third party application with Python API from http://www.csie.ntu.edu.tw/~cjlin/libsvm/

@author: Norman MacDonald
@date: 2010-02-16
"""

import time
from pica.classifiers.BaseClassifier import BaseClassifier
from pica.ClassificationResults import ClassificationResults

class libSVMClassifier(BaseClassifier):
	"""libSVM Classification implementation."""

	def __init__(self,parameters_filename=None):
		self.parameters = {}
		if parameters_filename:
			self.parameters.update(self.load_parameters(parameters_filename)) #use inherited parameter IO
		self.null_flag = "NULL"
		
	def load_model(self,model_filename):
		return None
		#load_rules(model)
		
	def test(self,lstSamples,model):
		"""Test the libSVM classifier on the sample set and return the ClassificationResults."""
		
		classification_results = ClassificationResults()
		#print "Testing on %d samples"%(len(lstSamples))
		for sample in lstSamples:
			#if sample.get_class_label() != self.null_flag:	# RVF
			if True: # RVF. Also classify the sample, if the class is previously unknown
				best_class, prob = self.classify(sample,model)
				classification_results.add_classification(sample.id,best_class,sample.get_class_label(), prob)
		return classification_results
	
	
	def classify(self,sample,model):
		"""Classify a single sample with the model."""
		sample_vector = [int(x) for x in sample.get_attribute_matrix()]
                #adding support for probability models!
                if model["svm_model"].probability == 1:
                    best_class_index, probs = model["svm_model"].predict_probability(sample_vector)
                    prob = probs[int(best_class_index)]
                else:
		    best_class_index = int(model["svm_model"].predict(sample_vector))
                    prob = "NA"
		return model["class_label_map_index"][int(best_class_index)], prob
		best_class_index = int(model["svm_model"].predict(sample_vector))
		return model["class_label_map_index"][best_class_index]
	
