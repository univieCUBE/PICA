"""
Rank samples by CWMI.

@author:  Norman MacDonald
@date: 2010-02-16
"""

from pica.featureselectors.BaseFeatureSelector import BaseFeatureSelector
from pica.AssociationRule import AssociationRule,AssociationRuleSet
from pica.io.FileIO import FileIO
from math import log as mathlog
from CWMILibrary import CWMILibrary
from copy import deepcopy

class CWMIRankFeatureSelector(BaseFeatureSelector):
	"""Return a ranked list of features from a sample set."""
	
	def __init__(self,confounders_filename,scores=["mi"],features_per_class=2,confounder="order",positive_class="YES"):
		self.confounders = self.load_confounders(confounders_filename)
		self.confounder = confounder
		self.features_per_class = int(float(features_per_class)/len(scores))
		self.scores = scores
		self.P_Y = None
		self.P_Z = None
		self.P_Y_Z = None
		self.positive_class = positive_class
		
	
	def load_confounders(self,confounder_filename):
		nfileio = FileIO()
		return nfileio.load_metadata(confounder_filename)
	
	def get_best_classes(self,attributes,sample_set):
		"""Return a list of classes where the class_labels are the best base on Laplace accuracy"""
		best = sample_set.get_best_laplace_accuracy(attributes)
		return [best[0]]
		
	def _get_class_labels(self,sample_set):
		class_labels = {}
		for sample in sample_set:
			class_labels[sample.get_class_label()] = 1
		return sorted(class_labels.keys())
	
	def select(self,sample_set):
		cwmilibrary = CWMILibrary()
		cwmilibrary.confounders = self.confounders
		ardic = {}
		nattributes = sample_set.get_number_of_features()
		confounder = self.confounder
		cwmilibrary.P_Y = None
		cwmilibrary.P_Y_Z = None
		cwmilibrary.P_Z = None
		for i in xrange(nattributes):
			#if i % 100 == 0:
			#	print "Processed %d of %d"%(i,nattributes)
			feature = i
			feature_scores = {}
			scores = cwmilibrary._calculate_information_scores(sample_set,feature,confounder)
			feature_scores["mi"] = scores["mi"]
			feature_scores["cmi"] = scores["cmi"]
			cwmi = 0.0
			if scores["hygivenz"] > 0:
				cwmi = float(scores["cmi"]*scores["mi"])/scores["hygivenz"]
			feature_scores["cwmi"] = cwmi
			
			#association_rule = AssociationRule([feature],["NULL"],feature_scores)
			if not ardic.has_key(feature):
				ardic[feature] = {}
			ardic[feature].update(feature_scores)
		#arlist[feature] = feature_scores
		association_rule_set = AssociationRuleSet()
		arlist = []
		for key in ardic.keys():
			class_labels = self.get_best_classes([key],sample_set)
			class_label = "NULL"
			if len(class_labels) >0:
				class_label = class_labels[0]
			arlist.append(AssociationRule([key],[class_label],ardic[key]))
		association_rule_set.extend(arlist)
		class_labels = self._get_class_labels(sample_set)
		
		association_rule_set = association_rule_set.remap_index_to_feature(sample_set)
		"Make several copies for each score, then switch back and forth between each until filled..."
		association_rule_sets = []
		for score in self.scores:
			aset = deepcopy(association_rule_set)
			aset.set_target_accuracy(score)
			association_rule_sets.append(aset)
		
		used_features = {}
		features = []
		features_to_select = self.features_per_class*len(self.scores)*len(class_labels)
		feature_class_counts = {}
		for score in self.scores:
			feature_class_counts[score] = {}
			for class_label in class_labels:
				feature_class_counts[score][class_label] = self.features_per_class
		print "Processing features (%d)"%(features_to_select)
		while features_to_select > 0:
			for score_index in xrange(len(self.scores)):
				score = self.scores[score_index]
				association_rule_set = association_rule_sets[score_index]
				"Pick the next rule for each class..."
				for class_label in class_labels:
					for rule_index in xrange(len(association_rule_set)):
						rule = association_rule_set[rule_index]
						if rule.rs[0] == class_label:
							if not used_features.has_key(rule.ls[0]):
								used_features[rule.ls[0]] = 1
								feature_class_counts[score][rule.rs[0]] -= 1
								features.append(rule.ls[0])
								features_to_select-=1
								break
		print "Finished processing for %s, found %d features"%(str(self.scores),len(features))
		if len(features) != self.features_per_class*len(scores)*len(class_labels):
			print "ERROR! did not find enough features...%d insead of %d"%(len(features),self.features_per_class*len(scores)*len(class_labels))
			
		return features
		
	
	