"""
Rank samples by CWMI, MI or somethign else.

@author:  Norman MacDonald
@date: 2010-02-16
"""

from pica.trainers.BaseTrainer import BaseTrainer
from pica.AssociationRule import AssociationRule,AssociationRuleSet
from pica.io.FileIO import FileIO
from math import log as mathlog
from CWMILibrary import CWMILibrary

class CWMIRankTrainer(BaseTrainer):
	"""Return a ranked list of features from a sample set."""
	
	def __init__(self,confounders_filename):
		print "Loading %s"%(confounders_filename)
		self.confounders = self.load_confounders(confounders_filename)
		print self.confounders.get_key_list()[1:]
		self.P_Y = None
		self.P_Z = None
		self.P_Y_Z = None
		
	def get_best_class(self,attributes,sample_set):
		"""Return a list of classes where the class_labels are the best base on Laplace accuracy"""
		best = sample_set.get_best_laplace_accuracy(attributes)
		return best[0]
		
	def load_confounders(self,confounder_filename):
		nfileio = FileIO()
		return nfileio.load_metadata(confounder_filename)
		
	
	def train(self,sample_set):
		cwmilibrary = CWMILibrary()
		cwmilibrary.confounders = self.confounders
		ardic = {}
		nattributes = sample_set.get_number_of_features()
		confounders = ["genus","family","order","class","phylum","superkingdom"]
		confounders = ["order"]
		cwmilibrary.P_Y = None
		for confounder in confounders:
			cwmilibrary.P_Y_Z = None
			cwmilibrary.P_Z = None
			for i in xrange(nattributes):
				if i % 100 == 0:
					print "Processed %d of %d"%(i,nattributes)
				feature = i
				feature_scores = {}
				scores = cwmilibrary._calculate_information_scores(sample_set,feature,confounder)
				feature_scores["%s_mi"%(confounder)] = scores["mi"]
				feature_scores["%s_cmi"%(confounder)] = scores["cmi"]
				cwmi = 0.0
				if scores["hygivenz"] > 0:
					cwmi = float(scores["cmi"]*scores["mi"])/scores["hygivenz"]
				feature_scores["%s_cwmi"%(confounder)] = cwmi
				
				if not ardic.has_key(feature):
					ardic[feature] = {}
				ardic[feature].update(feature_scores)
		association_rule_set = AssociationRuleSet()
		arlist = []
		for key in ardic.keys():
			class_label = self.get_best_class([key],sample_set)
			arlist.append(AssociationRule([key],[class_label],ardic[key]))
		association_rule_set.extend(arlist)
		association_rule_set = association_rule_set.remap_index_to_feature(sample_set)
		return association_rule_set
		
	
	