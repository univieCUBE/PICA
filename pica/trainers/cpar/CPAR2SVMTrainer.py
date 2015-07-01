"""
Implementation of the CPAR training algorithm.

This file only deals with numeric features.

@author: Norman MacDonald
@date: 2010-02-16
"""
import time
from PNData import *
from pica.utils.Log import log
from pica.trainers.BaseTrainer import BaseTrainer
from pica.AssociationRule import AssociationRuleSet
from CPARTrainer import CPARTrainer
from pica.trainers.libsvm.libSVMTrainer import libSVMTrainer
from copy import deepcopy
import os 


class CPAR2SVMTrainer(BaseTrainer):
	"""Main class for the CPAR implementation"""
	def __init__(self,parameters=None):
		self.parameters = parameters
		pass
		
	def remap_index_to_feature(self,association_rule_set,sample_set):
		return association_rule_set.remap_index_to_feature(sample_set)
	
	def remap_feature_to_index(self,association_rule_set,sample_set):
		return association_rule_set.remap_feature_to_index(sample_set)
	
	
	
	
	def train(self,samples):
		"""Train with CPAR on the sample set, returning an AssociationRuleSet."""
		current_class = samples.get_current_class()
		""" original. changed by RVF, see below...
		print "TRAINER FOUND PARAMETERS FROM %s"%(self.parameters)
		svm_trainer = libSVMTrainer(self.parameters)
		cpar_trainer = CPARTrainer(self.parameters)
		"""
		
		if self.parameters == None:
			print "Using standard parameters. "
		elif os.path.isfile(self.parameters):
			print "TRAINER FOUND PARAMETERS FROM %s"%(self.parameters)
		else:
			print "Trainer DID NOT find %s"%(self.parameters)
		svm_trainer = libSVMTrainer(self.parameters)
		cpar_trainer = CPARTrainer(self.parameters)
		
		arset = cpar_trainer.train(samples)
		print "Found %d rules!"%(len(arset))
		distinct_items = {}
		for rule in arset:
			for item in rule.ls:
				distinct_items[item] = 1
		print "Found %d distinct items"%(len(distinct_items.keys()))
		sample_set_feature_selected = samples.feature_select(distinct_items.keys())
		sample_set_feature_selected.set_current_class(current_class)
		non_zero_features = {}
		class_labels = {}
		for sample in sample_set_feature_selected:
			for item in nonzero(sample.get_attribute_matrix())[0]:
				non_zero_features[int(item)] = 1
			class_labels[sample.get_class_label()] = 1
		print "Using %d features with SVM classifier over %s (%d) class labels."%(len(non_zero_features.keys()),str(class_labels.keys()),len(class_labels.keys()))
		
		model = svm_trainer.train(sample_set_feature_selected)
		
		return model
	
