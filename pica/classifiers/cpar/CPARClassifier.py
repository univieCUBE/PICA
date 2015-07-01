"""
Implementation of the CPAR Classification implementation developed by Yin and Han, SDM, 2003.

@author: Norman MacDonald
@date: 2010-02-16
"""

import time
from pica.classifiers.BaseClassifier import BaseClassifier
from pica.ClassificationResults import ClassificationResults
from pica.AssociationRule import load_rules

class CPARClassifier(BaseClassifier):
	"""CPAR Classification implementation."""

	def __init__(self,parameters_filename=None,k=5,accuracy_measure="laplace"):
		self.parameters = {"k":k,"accuracy_measure":accuracy_measure}
		if parameters_filename:
			self.parameters.update(self.load_parameters(parameters_filename)) #use inherited parameter IO
		
	def load_model(self,model_filename):
		return load_rules(model)
		
	def test(self,lstSamples,model,confusionMatrix={}):
		"""Test the CPAR classifier on the sample set and return the ClassificationResults."""
		self.rules = model
		self.rules.set_target_accuracy(self.parameters["accuracy_measure"])
		lstRules = self.rules.remap_feature_to_index(lstSamples)
		if len(lstRules) ==0:
			return 0
		classification_results = ClassificationResults()
		print "Testing on %d samples"%(len(lstSamples))
		for sample in lstSamples:
			#if sample.get_class_label() != self.null_flag: # uncommented by RVF
			if True: # RVF. Also classify the sample, if the class is previously unknown
				intBestClass = self.classify(sample,lstRules)
				classification_results.add_classification(sample.id,intBestClass,sample.get_class_label())

		return classification_results
	
	
	def classify(self,sample,rules):
		"""Classify a single sample with the AssocationRuleSet."""
		relevant_rules = sample.get_relevant_k_rules(rules,self.parameters["k"])
		hshAverageAccuracies = self._get_average_accuracies(relevant_rules)
		return self._classify_based_on_average_accuracy(hshAverageAccuracies)
		
	def _classify_based_on_average_accuracy(self,hshAverageAccuracies):
		dblMax = -1
		best_label = None
		for label in hshAverageAccuracies.keys():
			if hshAverageAccuracies[label] > dblMax:
				dblMax = hshAverageAccuracies[label]
				best_label = label
		return best_label #its a tuple
	
	
	def _get_average_accuracies(self,lstRules):
		hshClassAccuracies = {}
		
		for rule in lstRules:
			if not hshClassAccuracies.has_key(rule.rs[0]):
				hshClassAccuracies[rule.rs[0]] =[0.0,0]        
			hshClassAccuracies[rule.rs[0]][0] += rule.accuracy
			hshClassAccuracies[rule.rs[0]][1] += 1
		hshAverageAccuracies = {}
		for key in hshClassAccuracies.keys():
			hshAverageAccuracies[key] = float(hshClassAccuracies[key][0])/float(hshClassAccuracies[key][1])
		return hshAverageAccuracies
