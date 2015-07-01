

from math import log as mathlog

class CWMILibrary():
	
	def __init__(self):
		self.P_Y = None
		self.P_Y_Z = None
		self.P_Z = None
	
	def _calculate_P_Y(self,sample_set):
		nsamples = len(sample_set)
		P_Y = {}
		#quick initialize instead of if statement
		for sample in sample_set:
			P_Y[sample.current_class_label] = 0
		for sample in sample_set:
			P_Y[sample.current_class_label]+=1
		for key in P_Y.keys():
			P_Y[key] = float(P_Y[key])/nsamples
		return P_Y
	
	def _calculate_P_Y_Z(self,sample_set,confounder):
		
		P_Y_Z ={}
		nsamples = len(sample_set)
		#Calculate entropy of phenotype with confounder:
		for sample in sample_set:
			Y = sample.current_class_label
			Z = self.confounders[sample.id][confounder]
			if not P_Y_Z.has_key((Y,Z)):
					P_Y_Z[(Y,Z)] = 0
			P_Y_Z[(Y,Z)] += 1
		for key in P_Y_Z.keys():
			P_Y_Z[key] = float(P_Y_Z[key])/float(nsamples)
		return P_Y_Z
		
	def _calculate_P_Z(self,sample_set,confounder):
		P_Z ={}
		nsamples = len(sample_set)
		for sample in sample_set:
			P_Z[self.confounders[sample.id][confounder]] = 0
		
		for sample in sample_set: #organism in range(0,len(self.confounders)):
			P_Z[self.confounders[sample.id][confounder]]+=1
		for key in P_Z.keys():
			P_Z[key] = float(P_Z[key])/float(nsamples)
		return P_Z
	
	def _calculate_mi(self,P_X,P_Y,P_X_Y):
		MI = 0.0
		for x in (0,1):
			for y in P_Y.keys():
				if P_X_Y[(x,y)] > 0:
					MI += P_X_Y[(x,y)]*(mathlog(P_X_Y[(x,y)],2) - mathlog((P_X[x]*P_Y[y]),2))
		return MI
	
	def _calculate_cmi(self,P_X,P_Y,P_Z,P_X_Y,P_X_Z,P_Y_Z,P_X_Y_Z):
		CMI =0.0
		for x in (0,1):
			for y in P_Y.keys():
				for z in P_Z.keys():
					if P_X_Y_Z.has_key((x,y,z)):
						if P_X_Y_Z[(x,y,z)]>0:
							CMI += P_X_Y_Z[(x,y,z)]*(mathlog(P_Z[z],2) + mathlog(P_X_Y_Z[(x,y,z)],2) - (mathlog(P_X_Z[(x,z)],2) +mathlog(P_Y_Z[(y,z)],2)))
		return CMI
	
	def _calculate_information_scores(self,sample_set,feature,confounder):
		#def getCMI(self,feature,lstSamples,lstConfounders,CONFOUNDERINDEX):
		nsamples = len(sample_set)
		if self.P_Y == None:
			self.P_Y = self._calculate_P_Y(sample_set)
		if self.P_Z == None:
			self.P_Z = self._calculate_P_Z(sample_set,confounder)
		if self.P_Y_Z == None:
			self.P_Y_Z = self._calculate_P_Y_Z(sample_set,confounder)
		
		P_Y = self.P_Y
		P_Z = self.P_Z
		P_Y_Z = self.P_Y_Z
		
		P_X = [0,0]
		X = [feature]
		for sample in sample_set:
			if sample.satisfies(X):
				P_X[1]+=1
			else:
				P_X[0]+=1
		for x in (0,1):
			P_X[x] = float(P_X[x])/float(nsamples)
		
		P_X_Y ={}
		for sample in sample_set:
			Y = sample.current_class_label
			if not P_X_Y.has_key((1,Y)):
					P_X_Y[(1,Y)] = 0
			if not P_X_Y.has_key((0,Y)):
					P_X_Y[(0,Y)] = 0
			if sample.satisfies(X):
				P_X_Y[(1,Y)] += 1
			else:
				P_X_Y[(0,Y)] += 1
		for key in P_X_Y.keys():
			P_X_Y[key] = float(P_X_Y[key])/float(nsamples)
		P_X_Z ={}
		
		for sample in sample_set:
			Z = self.confounders[sample.id][confounder]
			if not P_X_Z.has_key((1,Z)):
					P_X_Z[(1,Z)] = 0
			if not P_X_Z.has_key((0,Z)):
					P_X_Z[(0,Z)] = 0
			if sample.satisfies(X):
				P_X_Z[(1,Z)] += 1
			else:
				P_X_Z[(0,Z)] += 1
				
		for key in P_X_Z.keys():
			P_X_Z[key] = float(P_X_Z[key])/float(nsamples)
		
		P_X_Y_Z={}
		#Calculate X,Y,Z entropy:
		for sample in sample_set:
			Y = sample.current_class_label
			Z = self.confounders[sample.id][confounder]
			if not P_X_Y_Z.has_key((1,Y,Z)):
					P_X_Y_Z[(1,Y,Z)] = 0
			if not P_X_Y_Z.has_key((0,Y,Z)):
					P_X_Y_Z[(0,Y,Z)] = 0
			if sample.satisfies(X):
				P_X_Y_Z[(1,Y,Z)] += 1
			else:
				P_X_Y_Z[(0,Y,Z)] += 1
			
		for key in P_X_Y_Z.keys():
			P_X_Y_Z[key] = float(P_X_Y_Z[key])/float(nsamples)
		
		H_Y_Given_Z = 0.0
		H_Y_Z = 0.0
		H_Z = 0.0
		for y in P_Y.keys():
			for z in P_Z.keys():
				if P_Y_Z.has_key((y,z)):
					if P_Y_Z[(y,z)] > 0:
						H_Y_Z += P_Y_Z[(y,z)]*(mathlog(P_Y_Z[(y,z)],2))
		for z in P_Z.keys():
			if P_Z[z] > 0:
				H_Z += P_Z[z]*(mathlog(P_Z[z],2))
		H_Y_Given_Z = -(H_Y_Z - H_Z)
		
		MI = self._calculate_mi(P_X,P_Y,P_X_Y)
		CMI = self._calculate_cmi(P_X,P_Y,P_Z,P_X_Y,P_X_Z,P_Y_Z,P_X_Y_Z)
		
		return_scores = {"mi":MI,"cmi":CMI,"hz":H_Z,"hyz":H_Y_Z,"hygivenz":H_Y_Given_Z,"px":P_X,"py":P_Y,"pz":P_Z,"pxy":P_X_Y,"pyz":P_Y_Z,"pxz":P_X_Z,"pxyz":P_X_Y_Z}
		return return_scores
	