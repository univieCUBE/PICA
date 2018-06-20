"""
A collection of samples.

@author: Norman MacDonald
@date: 2010-02-16
"""

from DataCollection import DataCollection
from numpy import zeros, nonzero, array, random, append
from copy import deepcopy
#import random

class Sample():
	"""A single sample composed of attributes and an id.""" 
	def __init__(self,who_string=None,attributes=None,parent_sample_set=None):
		"""Initialize the sample with an id, feature/attribute set, and parent sample set."""
		self.dblWeight = 1.0
		self._attributes_matrix = None
		self.id = None
		self.class_labels = {}
		self.current_class_label = None
		self.parent_sample_set = parent_sample_set
                #self.parent_sample_set = None		

		if not attributes is None: #if copying, do not initialize
			#attributes.sort() #why sorting attributes?
			self.id = who_string
			self._attributes_matrix = zeros(parent_sample_set.max_attribute+1,dtype="bool_")
			for i in attributes:
				self._attributes_matrix[i] = 1
				
			
	def get_attributes_string_list(self):
		"""Return a list of attribute strings that are present."""
		index_to_feature = self.parent_sample_set.index_to_feature
		return [index_to_feature[i] for i in self.get_attributes_index_list()]
		
	
	def get_attributes_index_list(self):
		"""Return a list of attribute indices that are present."""
		return nonzero(self._attributes_matrix)[0] #non zero along first dimension
		
	def get_attribute_matrix(self):
		"""Return an integer numpy vector of presence and absence of attributes (1 and 0)"""
		return self._attributes_matrix
	
	def satisfies(self,antecedent):
		"""Return True if and only if all of the indices in the antecedent list are present in the sample."""
		am = self._attributes_matrix
		return len(filter(lambda i: am[i]==0,antecedent))==0
		
	
	def get_relevant_k_rules(self,lstRules,k):
		"""Return the top K rules from each class label where this sample satisfies the antecedent."""
		lstNewRules = []
		hshClassCounter = {}
		for rule in lstRules:
			if self.satisfies(rule.ls):
				if not hshClassCounter.has_key(rule.rs[0]):
					hshClassCounter[rule.rs[0]] = 0
				hshClassCounter[rule.rs[0]] += 1
				if hshClassCounter[rule.rs[0]] <= k:
					lstNewRules.append(rule)            
		return lstNewRules
	

		
	def get_class_label(self,target_class=None):
		"""Return the string label for this sample for the given class, or the current class."""
		if target_class==None:
			return self.current_class_label
			#return self.class_labels[self.parent_sample_set.current_class]
		return self.class_labels[target_class]

	def relabel(self,attribute,label):
		"""DEPRECATED?  Relabel this sample with the given label."""
		ret = Sample()
		ret.dblWeight = self.dblWeight
		
		ret.intClass = label
		
		ret._lstAttributes = deepcopy(self._lstAttributes)
		ret._lstAttributesKeys = deepcopy(self._lstAttributesKeys)
		ret._matAttributesKeys = deepcopy(self._matAttributesKeys)
		
		if ret._matAttributesKeys[attribute]==1:
			del ret._lstAttributes[attribute]
			ret._lstAttributesKeys.remove(attribute)
			ret._matAttributesKeys[attribute] = 0
		return ret
		
	def __deepcopy__(self,memo):
		"""Override deepcopy in order to copy the attribute matrix by reference for performance reasons."""
		"Override copy implementation"
		ret = Sample() # create a new sample and copy by value weight and class
		ret.dblWeight = self.dblWeight
		ret.id = self.id
		ret.class_labels = self.class_labels
		ret.current_class_label = self.current_class_label
		ret.parent_sample_set =self.parent_sample_set
		
		ret._attributes_matrix = self._attributes_matrix #reference copy of dictionary entries, as they should never be modified
		return ret
	
	def is_null_class(self,target=None):
		"""Returns true if target class is null.  If target is not provided, returns true if all classes are null."""
		
		retval = True
		if target == None:
			#for c in self.parent_sample_set.class_label_set.get_classes():
			#	if not self.is_null_class(c):
			#		retval = False
                        retval = True
		else:
			if not self.get_class_label(target) == self.parent_sample_set.null_flag:
				retval = False
		return retval

	
class SampleSet():
	"""A set of Samples."""
	def __init__(self,max_attribute):
		"""Initialize a sample set with the number of attributes."""
		self.max_attribute = max_attribute
		self.indexed_samples = []
		self.index_to_feature = []
		self.feature_to_index = {}
		self.class_label_set = None
		self.current_class = None
		self.null_flag = "NULL"
		self.all_samples = None
		
	def add_sample(self, who_string, attributes_matrix):
		"""Append a new sample with a given identifier and numpy attribute matrix."""
                if not self.get_by_id(who_string):
		    self.indexed_samples.append(Sample(who_string,attributes_matrix,self))
		
	def load_class_labels(self,class_label_set):
		"""Load the class labels to each of the relevant samples."""
		self.class_label_set = class_label_set
		for sample in self.indexed_samples:
			sample.class_labels = class_label_set[sample.id]
			
	def set_current_class(self,target_class):
		"""Set the default class for all samples."""
		self.current_class = target_class
		#for performance reasons, run through and set class to each sample
		for sample in self:
			sample.current_class_label = sample.class_labels[target_class]
	
	def get_feature_to_index(self):
		"""Get feature_to_index dictionary that maps COG/NOG/etc to index (dimension in case of SVM)"""
		return self.feature_to_index
	
	def get_index_to_feature(self):
		"""Get index_to_feature list that maps index to COG/NOG/etc"""
		return self.index_to_feature
	
	def get_class_labels(self,target_class=None):
		class_labels = {}
		for sample in self:
			class_labels[sample.get_class_label(target_class)] = 1
		return sorted(class_labels.keys())
	
	def get_current_class(self):
		return self.current_class
	
	def get_number_of_features(self):
		"""Return the number of features."""
		return len(self.index_to_feature)
		
	def __iter__(self):
		"""Return an iterator to the samples."""
		return self.indexed_samples.__iter__()
	
	def __getitem__(self,key):
		"""Get a sample by id."""
		return self.indexed_samples[key]
	
	def __delitem__(self,key):
		"""Delete a sample by id."""
		del self.indexed_samples[key]
	
	def __len__(self):
		"""Return the number of samples."""
		return len(self.indexed_samples)
	
	def get_by_id(self,identifier):
		for sample in self.indexed_samples:
			if sample.id == identifier:
				return sample
		return None
	
	def get_best_laplace_accuracy(self,items,target_class=None):
		laplace = self.get_laplace_accuracy(items,target_class)
		best_tuples = [tuple((laplace[x],x)) for x in laplace.keys()]
		best_tuples.sort(reverse=True)
		if len(best_tuples) > 0:
			return tuple((best_tuples[0][1],best_tuples[0][0]))
		else:
			return tuple(("None",0))
		
	
	def get_laplace_accuracy(self,items,target_class=None):
		"""Return the Laplace accuracy (1-Laplace error) for a given set of attributes for each class label."""
		feature_class_counts = self.get_class_label_distribution(items,target_class)
		laplace = {}
		ntot = 0
		for f in feature_class_counts.keys():
			ntot += feature_class_counts[f]
		class_labels = sorted(feature_class_counts.keys())
		for class_label in class_labels:
			laplace[class_label] = (float(feature_class_counts.get(class_label,0)+1.0)/float(ntot+len(class_labels)))
		return laplace
	
	def get_class_label_distribution(self,items=None,target_class = None):
		class_label_counts = {}
		for sample in self:
			if items and not sample.satisfies(items):
				continue
			class_label = sample.get_class_label(target_class)
			if not class_label_counts.has_key(class_label):
				class_label_counts[class_label] = 0
			class_label_counts[class_label] += 1
		return class_label_counts
	
	def remove_by_null_class(self,target=None):
		"""Remove samples with target of NULL. If target is None, all samples that have no non-null class info are removed."""
		null_flagged = []
		i = 0
		for i in range(len(self.indexed_samples)):
			sample = self[i]
			if sample.is_null_class(target):
				null_flagged.append(i)
		null_flagged.sort(reverse=True)
		for index in null_flagged:
			del self[index]
	def hide_nulls(self,target=None):
		"""Hide samples with target of NULL. If target is None, all samples that have no non-null class info are hidden."""
		if self.all_samples == None:
			self.all_samples = deepcopy(self.indexed_samples)
		else:
			self.indexed_samples = deepcopy(self.all_samples)
		self.remove_by_null_class(target)
		
	def unhide_all(self):
		"""Unhide all samples."""
		if self.all_samples != None:
			self.indexed_samples = self.all_samples
		
	
	def _is_equal(self,vectora,vectorb):
		"""Check for equality.
		
		There are many methods of checking for equality.  This one is fast for those that are not expected
		to be equal.
		"""
		gridcount = 0
		isequal = True
		while gridcount < len(vectora):
			if vectora[gridcount] != vectorb[gridcount]:
				isequal = False
				break
			gridcount += 1
		return isequal
	
        def induce_incompleteness(self,percent):

                if percent==1.0:
                    return self
                newsampleset = SampleSet(self.max_attribute)
                newsampleset.feature_to_index = self.feature_to_index
                newsampleset.index_to_feature = self.index_to_feature


                for sample in self.__iter__():
                    attribute_list=sample.get_attributes_index_list()
                    num_of_features=int(round(len(attribute_list)*percent))
                    new_attribute_list=random.choice(attribute_list,num_of_features,replace=False)

                    newsampleset.add_sample(sample.id,new_attribute_list)

                newsampleset.load_class_labels(self.class_label_set)
                newsampleset.set_current_class(self.current_class)

                return newsampleset

        def introduce_contamination(self,collection,percent):

                if percent==0:
                    return self
                newsampleset = SampleSet(self.max_attribute)
                newsampleset.feature_to_index = self.feature_to_index
                newsampleset.index_to_feature = self.index_to_feature

                contaminate_with={}
                collection_sizes={}
                all_class_labels=collection.keys()

                #TODO: implement a solution for multi class svm, not urgent
                assert (len(all_class_labels)==2, "More than 2 classes (YES/NO) cannot be contaminated at the moment")
                collection_sizes[all_class_labels[0]]=len(collection[all_class_labels[1]])
                collection_sizes[all_class_labels[1]]=len(collection[all_class_labels[0]])

                contaminate_with[all_class_labels[0]]=all_class_labels[1]
                contaminate_with[all_class_labels[1]]=all_class_labels[0]

                for sample in self.__iter__():
                    new_attribute_list = sample.get_attributes_index_list()
                    #add contamination from test set. exactly X% of features of one sample (allowing doubles):
                    contamination_sample=collection[contaminate_with[sample.current_class_label]][random.randint(collection_sizes[sample.current_class_label])]
                    if percent<1.0:
                        add_num=int(round(len(contamination_sample)*percent,0))
                        new_attribute_list=append(new_attribute_list,random.choice(contamination_sample,add_num,replace=False))
                    else:
                        new_attribute_list=append(new_attribute_list,contamination_sample)

                    #removing doubles not needed! create new sample
                    newsampleset.add_sample(sample.id,new_attribute_list)

                newsampleset.load_class_labels(self.class_label_set)
                newsampleset.set_current_class(self.current_class)

                return newsampleset

        def map_test_set_attributes_to_training_set(self,training_set):

                newsampleset = SampleSet(training_set.max_attribute)
                newsampleset.index_to_feature = training_set.index_to_feature
                newsampleset.feature_to_index = {}
                for attribute in training_set.feature_to_index:
                    index=training_set.feature_to_index[attribute]
                    attribute_split=attribute.split("/")
                    for attribute in attribute_split:
                        newsampleset.feature_to_index[attribute]=index

                for sample in self.__iter__():
                    attribute_index_list=[]
                    attribute_string_list=sample.get_attributes_string_list()
                    for attribute_string in attribute_string_list:
                        attribute_index_list.append(newsampleset.feature_to_index[attribute_string])

                    newsampleset.add_sample(sample.id,array(attribute_index_list))

                newsampleset.load_class_labels(self.class_label_set)
                newsampleset.set_current_class(self.current_class)

                return newsampleset

        def _sort_by_sample_set(self,reference_set):

                newsampleset = SampleSet(self.max_attribute)
                newsampleset.index_to_feature = self.index_to_feature
                newsampleset.feature_to_index = self.feature_to_index
                newsampleset.all_samples=[]
                newsampleset.indexed_samples=[]
                

                for ref_sample in reference_set:
                    sample=self.get_by_id(ref_sample.id)
                    newsampleset.indexed_samples.append(sample)

                newsampleset.class_label_set = self.class_label_set
                newsampleset.current_class = self.current_class

                return newsampleset



	def compress_features(self):
		"""Compress features with identical profiles into single features in a new sample set."""
		grid = self.build_numpy_grid()
		#compressed_list = {}
		i = 0
		#newindex = 0
		newfeature_to_index = {}
		newindex_to_feature = []
		gridlen = len(grid[0,:])
		dicgridsums = {}
		print "Computing hash of unique feature profiles...",
		for i in range(gridlen):
			ccolumn = grid[:,i]
			thekey = tuple(ccolumn)
			if not dicgridsums.has_key(thekey):
				dicgridsums[thekey] = []
			dicgridsums[thekey].append(i)
		print "found %d distinct clusters."%(len(dicgridsums.keys()))
		newindex = 0
		
		# find matches in each group.
		compressed = {}
		cluster_index = 0
		newindex_to_oldindex = {}
		for key in dicgridsums.keys():
			for i in range(len(dicgridsums[key])):
				itema = dicgridsums[key][i]
				if not compressed.has_key(itema):
					compressed[itema] = newindex
					newindex_to_feature.append([])
					newindex_to_feature[newindex].append(self.index_to_feature[itema])
					newindex_to_oldindex[newindex] = itema
					for item in dicgridsums[key][i+1:]:
						isEqual = self._is_equal(grid[:,itema],grid[:,item])
						if isEqual:
							compressed[item] = newindex
							newindex_to_feature[newindex].append(self.index_to_feature[item])
					newindex += 1
			cluster_index += 1
		
		nunique_items = len(dicgridsums.keys())
		
		str_newindex_to_feature = []
		print "Reduced from %d to %d features (nuniqueitems:%d)"%(len(self.index_to_feature),len(newindex_to_feature),nunique_items)
		for i in range(nunique_items):
			newindex_to_feature[i].sort()
			newfeature = "/".join([str(x) for x in newindex_to_feature[i]])
			str_newindex_to_feature.append(newfeature)
			newfeature_to_index[newfeature] = i
		
		
		newgrid = zeros((len(self.indexed_samples),nunique_items),dtype="bool_")
		i=0
		while i < nunique_items:
			newgrid[:,i] = grid[:,newindex_to_oldindex[i]]
			i += 1
		newsampleset = SampleSet(nunique_items-1)
		newsampleset.feature_to_index = newfeature_to_index
		newsampleset.index_to_feature = str_newindex_to_feature
		#samples = [] 
		for j in range(len(self.indexed_samples)):
			nonzeroindices = nonzero(newgrid[j,:]) # along the first dimension
			#for n in nonzeroindices[0]:
			#	print n
			#attributes = map(lambda f: newsampleset.index_to_feature[f],nonzeroindices[0])
			newsampleset.add_sample(self[j].id,nonzeroindices[0])
			
		newsampleset.load_class_labels(self.class_label_set)
		
		return newsampleset
		
		
	def build_numpy_grid(self):
		"""Build a numpy grid from the attribute vectors of each sample."""
		grid = zeros((len(self.indexed_samples),self.max_attribute+1),dtype="bool_")
		for i in range(len(self.indexed_samples)):
			grid[i,:] = array(self[i].get_attribute_matrix())>0
		return grid
	
	def randomize(self):
		random.shuffle(self.indexed_samples)
		
	def subset(self,index_list_list=None):
		"""
		Returns a new sample set covering the indexed samples.
		
		index_list_list is a list of two element lists of start and end indices
		"""
		newsubset = SampleSet(self.max_attribute)
		newsubset.indexed_samples = []
		newsubset.all_samples = []
                if index_list_list:
		    for l in index_list_list:
			newsubset.all_samples.extend(self.all_samples[l[0]:l[1]])
			newsubset.indexed_samples.extend(self.indexed_samples[l[0]:l[1]])
                else:
                        newsubset.all_samples.extend(self.all_samples[:])
                        newsubset.indexed_samples.extend(self.indexed_samples[:])
		
		newsubset.index_to_feature = self.index_to_feature
		newsubset.feature_to_index = self.feature_to_index
		newsubset.class_label_set = self.class_label_set
		newsubset.current_class = self.current_class
		newsubset.null_flag = "NULL"
		
		return newsubset
		
	def feature_select(self, features):
		"""Output a sample set but only include features in feature_set.
		
		"""
		#get indices for features:
		new_sample_set = deepcopy(self)
		indexed_features = [self.feature_to_index[feature] for feature in features]
		print "Selecting %d features"%(len(indexed_features))
		for sample in new_sample_set:
			new_features = zeros(len(sample.get_attribute_matrix()),dtype="bool_")
			for feature_zero_index in xrange(len(indexed_features)):
				if sample.satisfies((indexed_features[feature_zero_index],)):
					new_features[indexed_features[feature_zero_index]] = 1
			sample._attributes_matrix = new_features
		return new_sample_set
class ClassLabelSet(DataCollection):
	"""Stores the class labels for the samples.
	
	Most of the methods are defined in the base class, DataCollection.
	"""
	def get_classes(self):
		"""Returns a list of classes."""
		return self.get_key_list()[1:]
