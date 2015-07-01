"""
Implementation of the Classification based on Predictive Association Rules (CPAR) training algorithm developed by Yin and Han, SDM, 2003.

This file only deals with numeric features.

@author: Norman MacDonald
@date: 2010-02-16
"""
import time
from PNData import *
from pica.utils.Log import log
from pica.trainers.BaseTrainer import BaseTrainer
from pica.AssociationRule import AssociationRuleSet


class CPARTrainer(BaseTrainer):
	"""Main class for the CPAR implementation"""
	def __init__(self,parameters=None):
		self.objPNData = None
		self.lstRules = [] 
		self.dblGainSimilarityRatio = 0.99
		self.dblTotalWeightFactor = 0.05
		self.dblDecayFactor = 2.0/3.0
		self.dblMinGainThreshold = 0.7
		self.intKValue = 5
		self.MAX_RULE_SIZE = 9999
	
	def remap_index_to_feature(self,association_rule_set,sample_set):
		return association_rule_set.remap_index_to_feature(sample_set)
	
	def remap_feature_to_index(self,association_rule_set,sample_set):
		return association_rule_set.remap_feature_to_index(sample_set)
			
	def train(self,samples,maxRuleSize=9999,mineOnlyClass=None):
		"""Train with CPAR on the sample set, returning an AssociationRuleSet."""
		self.MAX_RULE_SIZE = maxRuleSize
		self.objPNData = PNData(samples)
		self.lstRules = []
		classes = self.objPNData.getClassList()
		
		log("Dataset has %d classes over %d samples."%(len(classes),len(samples)))
		for current_class in classes:
			if mineOnlyClass != None:
				if current_class != mineOnlyClass:
					continue
			log("Processing class %s"%(current_class))
			self.objPNData.setCurrentClass(current_class)
			dblMinTotalWeight = self.dblTotalWeightFactor * self.objPNData.getTotalWeight()
			lstAntecedent = []
			while self.objPNData.getTotalWeight() > dblMinTotalWeight:
				self.objPNData.refreshPNAData()
				if self.objPNData.noValidGainsinPNarray(self.dblMinGainThreshold):
					#log("NO VALID GAINS....Breaking!"); 
					break
				#log('BEGIN DEPTH FIRST SEARCH - total weight %f > %f'%(self.objPNData.getTotalWeight(),dblMinTotalWeight))
				self._CPARdfs(self.objPNData.copyPrimes(),lstAntecedent,[current_class])
		trules = len(self.lstRules)
		self.removeDuplicateRules()
		#log("End of rule search. Found %d rules total, %d after duplicates removed."%(trules,len(self.lstRules)))
		arset = AssociationRuleSet()
		arset.extend(self.lstRules)
		arset.set_target_accuracy("laplace")
		return self.remap_index_to_feature(arset,samples)

		
				
	def _CPARdfs(self,objPNDatacopy,lstAntecedent,lstConsequent):
		"""Depth first search for constructing a new rule."""
		blnMaxExceeded = False
		if (len(lstAntecedent) == self.MAX_RULE_SIZE):
			blnMaxExceeded = True
		'GET ALL ATTRIBUTES WITHIN 1.0 - dblGainSimilarityRatio of max'
		objPNDatacopy.recalculateGains()
		[dblGain,lstAttributes] = objPNDatacopy.getBestGainAttributes(self.dblGainSimilarityRatio)
		if dblGain > self.dblMinGainThreshold and not blnMaxExceeded:
			for intAttribute in lstAttributes:
				"""
				This is a check to see if this attribute still within 1%...it may not
				after the depth first search
				"""
				lstAntecedentCopy = deepcopy(lstAntecedent)
				lstAntecedentCopy.append(intAttribute)
				objPNDatacopyTemp = objPNDatacopy.copyPrimes()
				objPNDatacopyTemp.lstAprime[intAttribute] = 0
				objPNDatacopyTemp.removeExamplesNotSatisfying(lstAntecedentCopy)
			
				self._CPARdfs(objPNDatacopyTemp,lstAntecedentCopy,lstConsequent)
		else:
			if len(lstAntecedent)>0:
				lstAntecedent.sort()
				dblLaPlaceAccuracy = self.objPNData.getLaPlaceAccuracy(lstAntecedent,lstConsequent)
				objRule = AssociationRule(lstAntecedent, lstConsequent, {"laplace":dblLaPlaceAccuracy})
				objPNDatacopy.updateWeights(objRule,self.dblDecayFactor)
				self.addRule(objRule)
			else:
				log("Empty antecedent.")
				pass
				
	
			
	def addRule(self,objRule):
		"""Add the rule to the AssociationRuleSet."""
		self.lstRules.append(objRule)
		#log("FOUND RULE: %s\n"%(str(objRule)))
		
	def removeDuplicateRules(self,objRule=None,startindex=0):
		"""Ensure that there are no duplicate rules."""
		if objRule==None:
			i = 0
			while i < len(self.lstRules):
				r = self.lstRules[i]
				self.removeDuplicateRules(r,i+1)
				i+=1
		else:
			i = startindex
			while i < len(self.lstRules):
				r = self.lstRules[i]
				if objRule.ls == r.ls and objRule.rs == r.rs:
					del self.lstRules[i]
					i-=1
				i+=1
