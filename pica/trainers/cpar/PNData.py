"""
Implementation of the PNArray structure used by the CPAR algorithm. (Yin and Han, SDM, 2003)

@author: Norman MacDonald
@date: 2010-02-16
"""

from math import log as mathlog
from pica.AssociationRule import *
from copy import deepcopy
from pica.utils.Log import log
from numpy import *
import sys

class PNData(object):
	"""Stores the Postive and Negative examples while the CPAR algorithm is executing."""
	
	
	def __init__(self,lstSamples=[]):
		"""Initialize with a SampleSet."""
		if len(lstSamples)>0:
			self.dblTotalWeight = 0
			self.dblPositiveWeight = 0
			self.dblNegativeWeight = 0
			self.lstSamples = lstSamples
			
			hshClasses = {}
			for objS in lstSamples:
				hshClasses[objS.get_class_label()] = 1
			self.lstClasses = hshClasses.keys()
			self.lstClasses.sort()
			#log("Just testing the log function...")
			
			
	def updatePN(self):
		"""Copy the main PN list with PNprime. See the CPAR paper for more details."""
		self.lstPN = self.lstPNprime.copy()
	
	def copyPrimes(self):
		"""Efficiently copy the PN data structure."""
		objCopy = PNData()
		#BY REFERENCE
		objCopy.lstSamples = self.lstSamples
		objCopy.lstClasses = self.lstClasses
		objCopy.lstP = self.lstP
		objCopy.lstN = self.lstN
		objCopy.lstPN = self.lstPN
		objCopy.lstA = self.lstA
		
		
		#BY VALUE
		objCopy.lstPprime = deepcopy(self.lstPprime)
		objCopy.lstNprime = deepcopy(self.lstNprime)
		objCopy.lstPNprime = self.lstPNprime.copy()
		objCopy.lstAprime = self.lstAprime[:]
		objCopy.lstAGainprime = self.lstAGainprime[:]
		return objCopy
		
	def getClassList(self):
		"""Return a list of class labels."""
		return self.lstClasses
	
	def setCurrentClass(self,intCurrentClass):
		"""Set the current class label, updating the positive and negative examples."""
		self.intCurrentClass = intCurrentClass
		self.lstP = []
		self.lstN = []
		nattributes = self.lstSamples.get_number_of_features()
		self.lstPN = zeros((nattributes,2),dtype=float)

		self.lstA = ones((nattributes),dtype=int)
		self.lstAGainprime = zeros((nattributes),dtype=float)

		i = 0
		for objS in self.lstSamples:
			i+=1
			objS.dblWeight = 1.0
			# bug: just don't use log() in this class...
			#log("setcurrentclass: Processing sample %d, checking for class %s"%(i,intCurrentClass))
			#log("x",False) #RVF for debugging purposes only ...
			if objS.get_class_label() == intCurrentClass:
				self.lstP.append(objS)
				sys.stdout.flush()
				self.lstPN[:,0] += objS.get_attribute_matrix()

			else:
				self.lstN.append(objS)
				self.lstPN[:,1] += objS.get_attribute_matrix()
							
			
		self.refreshPNAData()
		
		
	
	def getTotalWeight(self):
		"""Get the remaining weight of the positive examples."""
		dblTotalWeight = 0.0
		for objP in self.lstP:
			dblTotalWeight += objP.dblWeight
		return dblTotalWeight 

	
	def refreshPNAData(self):
		"""Re-initialize the PN data structure (after a rule search is complete)."""
		self.lstNprime = deepcopy(self.lstN)
		self.lstPprime = deepcopy(self.lstP)
		self.lstAprime = self.lstA[:]
		self.lstPNprime = self.lstPN.copy()

		
	def getWeightOfPositiveExamples(self):
		"""Get the stored weight of the remaining positive examples."""
		return self.dblPositiveWeight
	
	def getWeightOfNegativeExamples(self):
		"""Get the stored weight of the remaining negative examples."""
		return self.dblNegativeWeight
	
	def getWeightOfExamples(self,ex):
		"""Calculate the weight of all examples (positive)."""
		dblTotalWeight = 0.0
		for objP in ex:
			dblTotalWeight += objP.dblWeight
		return dblTotalWeight
	
	def getBestGainAttributes(self,dblGainSimilarityRatio=99.0,dblMinBestGainThreshold=0.7):
		"""Return the attributes with the best gain (within dblGainSimilarityRatio of the best)."""
		dblBestGain = -1.0
		dblCurrentGain = -1.0
		intAttribute = -1

		self.lstAGainprime = self.lstAGainprime * self.lstAprime
		dblBestGain = max(self.lstAGainprime)
		
		dblGainThreshold = dblGainSimilarityRatio * dblBestGain
		if dblGainThreshold <= dblMinBestGainThreshold: 
			dblGainThreshold = dblMinBestGainThreshold
		if dblBestGain > 0:
			lstAttributes = where(self.lstAGainprime > dblGainThreshold)[0]#filter(lambda i: self.lstAGainprime[i]>dblGainThreshold,range(1,len(self.lstAprime)))
		else:
			lstAttributes = []
		
		return [dblBestGain,lstAttributes]
	

	def removeExamplesNotSatisfying(self,antecedent):
		"""Update the positive and negative examples with those that apply to the antecedent of the current rule."""
		newlstPprime = []
		append = newlstPprime.append
		for objP in self.lstPprime:
			if objP.satisfies(antecedent):
				append(objP)
					
			else:
				self.lstPNprime[:,0]-= (objP.dblWeight*objP.get_attribute_matrix())

		self.lstPprime = newlstPprime
		
		if len(self.lstPprime)==0:
			self.lstPNprime[:,0] = 0.0

		newlstNprime = []
		append = newlstNprime.append
		for objN in self.lstNprime:

			if objN.satisfies(antecedent):
				append(objN)
			else: 
				self.lstPNprime[:,1]-=(objN.dblWeight*objN.get_attribute_matrix())

		self.lstNprime = newlstNprime
		if len(self.lstNprime)==0:
			self.lstPNprime[:,1] = 0.0

	
	def getAccuracyMeasure(self,lstAntecedent,lstConsequent):
		"""Layer of indirection for finding the accuracy measure."""
		return getLaPlaceAccuracy(self,lstAntecedent,lstConsequent) 

	def getLaPlaceAccuracy(self,lstAntecedent,lstConsequent):
		"""Return the Laplace accuracy for the given antecedent and consequent."""
		nc = 0
		ntot = 0
		for objS in self.lstSamples:
			if objS.satisfies(lstAntecedent):
				ntot+=1
				if lstConsequent[0] == objS.get_class_label():
					nc+=1
		return (float((nc+1)))/float((ntot+len(self.lstClasses)))
	

	
	def updateWeights(self,objRule,dblDecayFactor):
		"""After a new rule is found, decay the weights of the samples that it covers."""
		for i in range(0,len(self.lstP)):
			objP = self.lstP[i]
			if objP.satisfies(objRule.ls):
				decay = dblDecayFactor*objP.dblWeight
				difference = objP.dblWeight - decay
				objP.dblWeight = decay
				self.lstPN[:,0] -= (difference*objP.get_attribute_matrix())

	def recalculateGains(self):
		"""Recalculate the gain for all of the attributes, if they were to be added to the current rule."""
		p = float(self.getWeightOfExamples(self.lstPprime))
		n = float(self.getWeightOfExamples(self.lstNprime))
		localmathlog = mathlog
		if p<=0 or p+n<=0:
			self.lstAGainprime[:] = 0.0
			return
		oldgain = localmathlog(p,2)-localmathlog(p+n,2)
		lstPNprime = self.lstPNprime
		lstAGainprime = self.lstAGainprime
		lenlstPNprime = len(self.lstPNprime)
		for intAttribute in xrange(0,lenlstPNprime):
			gain = 0.0
			pprime = lstPNprime[intAttribute][0]
			nprime = lstPNprime[intAttribute][1]
			if  (pprime > 0 and pprime+nprime > 0):
				gain = pprime *(localmathlog(pprime,2) - localmathlog(pprime+nprime,2) - oldgain)
			lstAGainprime[intAttribute] = gain
				
				
			
	def getGainForAttribute(self,intAttribute):
		"""Return the stored gain for a given attribute."""
		return self.lstAGainprime[intAttribute]

	def _getGain(self,pprime,nprime,p,n):
		"""Return gain."""
		if pprime <= 0 or p<=0:  return 0
		if p+n<=0 or pprime+nprime<=0: return 0
		return float(pprime)*(mathlog(float(pprime)/(pprime + nprime),2)-mathlog(float(p)/(p + n),2))
	
	def noValidGainsinPNarray(self,dblMinGainThreshold):
		"""Return true if maximum gain is less than the threshold."""
		p = float(self.getWeightOfExamples(self.lstPprime))
		n = float(self.getWeightOfExamples(self.lstNprime))

		if p<=0 or p+n<=0:
			return True
		oldgain = mathlog(float(p),2) - mathlog(p+n,2)
		for intAttribute in range(0,len(self.lstPNprime)):
			if self.lstAprime[intAttribute]==1:
				gain = 0.0
				pprime = float(self.lstPNprime[intAttribute][0])
				nprime = float(self.lstPNprime[intAttribute][1])
				if not (pprime <= 0 or pprime+nprime<=0):
					gain = pprime *((mathlog(pprime,2)- mathlog(pprime+nprime,2)) - oldgain)
				if gain > dblMinGainThreshold:
					return False
		return True
				

	def sortRulesByLaplace(self,lstRules):
		"""Sort rules by accuracy.  DEPRECATED."""
		lstNewRules = []
		while len(lstRules) >0:
			ruleindex = -1
			i=0
			crule = None
			maxLaPlace = -1
			for rule in lstRules:
				if rule.LaPlaceAccuracy > maxLaPlace:
					maxLaPlace = rule.LaPlaceAccuracy
					crule = rule
					ruleindex = i
				i+=1
			lstNewRules.append(crule)
			del lstRules[ruleindex]
		lstRules = lstNewRules #update pointer
		return lstRules
	
