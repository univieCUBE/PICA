"""
Handle libSVM file IO.

@author: Norman MacDonald
@date: 2010-02-16
"""

import sys
from pica.Sample import Sample, SampleSet, ClassLabelSet

class SVMIO:
	"""Handle libSVM IO."""
	def index(self,map_filename,sample_set):
		"""
		Take a genotype data structure and output an SVM map file
		index\tfeature
		
		e.g.
		14	COG3242,COG1123
		"""
		svm_index_to_feature = [x+1 for x in range(len(sample_set.index_to_feature))]
		fout = open(map_filename,"w")
		for x in range(len(sample_set.index_to_feature)):
			fout.write("%d\t%s\n"%(x+1,sample_set.index_to_feature[x]))
		fout.close()
	
	def cpar2svm(self,input_map_filename,filename,sample_set,target_class):
		"""Output an libSVM features file from a given map, sample set, and class."""
		
		index_to_feature = {}
		feature_to_index = {}
		fmap = open(input_map_filename)
		data = fmap.readlines()
		for line in data:
			fields = [x.strip() for x in line.split("\t")]
			index_to_feature[fields[0]]=fields[1]
			feature_to_index[fields[1]]=fields[0]
		fmap.close()
		out_lines = []
		#get non-null samples
		organisms = []
		for sample in sample_set:
			if sample.get_class_label(target_class) != "NULL":
				organisms.append(sample)
		#get indices for features:
		
		for sample in organisms:
			out_line = []
			if sample.get_class_label(target_class) == "YES":
				class_label = 1
			else:
				class_label = 0
			out_line.append("%+d"%(class_label))
			svm_features = []
			for feature_zero_index in range(len(sample.get_attribute_matrix())):
				feature_one_index = feature_zero_index + 1
				if sample.get_attribute_matrix()[feature_zero_index] == 1:
					svm_feature = int(feature_to_index[sample_set.index_to_feature[feature_zero_index]])
					svm_features.append(svm_feature)
			svm_features.sort()
			for svm_feature in svm_features:
				out_line.append("%d:1"%(svm_feature))
			out_lines.append(" ".join(out_line))
		
		fout = open(filename,"w")
		fout.write("\n".join(out_lines))
		fout.write("\n")
		fout.close()
	
	
	
	def filter(self,input_map_filename,filename,sample_set,target_class,rule_set):
		"""Output a libSVM features file (same as cpar2svm), but only include features in rule_set.
		
		Each rule in rule_set is broken down into its component items and used to filter the sample set.
		"""
		index_to_feature = {}
		feature_to_index = {}
		fmap = open(input_map_filename)
		data = fmap.readlines()
		for line in data:
			fields = [x.strip() for x in line.split("\t")]
			index_to_feature[fields[0]]=fields[1]
			feature_to_index[fields[1]]=fields[0]
		fmap.close()
		
		
		
		out_lines = []
		#get non-null samples
		organisms = []
		for sample in sample_set:
			if sample.get_class_label(target_class) != "NULL":
				organisms.append(sample)
		#get indices for features:
		remapped_rules = rule_set.remap_feature_to_index(sample_set)
		features = []
		indexed_features = []
		found_features = {}
		for i in range(len(rule_set)):
			rule = rule_set[i]
			indexed_rule = remapped_rules[i]
			#print rule.ls
			for j in range(len(rule.ls)):
				tls = rule.ls[j]
				for item in [x.strip() for x in tls.split("/")]:
					indexed_item = sample_set.feature_to_index.get(item,"X_NULL_X")

					if not indexed_item == "X_NULL_X" and not found_features.has_key(item):
						found_features[item] = 1
						#remap item HERE
						features.append((item,))
						indexed_features.append((indexed_item,))

		
		for sample in organisms:
			out_line = []
			if sample.get_class_label(target_class) == "YES":
				class_label = 1
			else:
				class_label = 0
			out_line.append("%+d"%(class_label))
			svm_features = []
			for feature_zero_index in range(len(indexed_features)):
				feature_one_index = feature_zero_index + 1
				svm_feature = int(feature_to_index[features[feature_zero_index][0]])
				if sample.satisfies(indexed_features[feature_zero_index]):
					svm_features.append(svm_feature)
			svm_features.sort()
			for svm_feature in svm_features:
				out_line.append("%d:1"%(svm_feature))
			out_lines.append(" ".join(out_line))
		
		fout = open(filename,"w")
		fout.write("\n".join(out_lines))
		fout.write("\n")
		fout.close()
		

	def save_to_svm(self,filename,map_filename,sample_set,target_class,rule_set):
		"""Index and filter based on the rule set, samples, and target class."""
		self.index(map_filename,sample_set)
		self.filter_svm(map_filename,filename,sample_set,target_class,rule_set)
		
