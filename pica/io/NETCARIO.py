"""
Perform IO on NETCAR files.

@author: Norman MacDonald
@date: 2010-02-16
"""

from pica.AssociationRule import AssociationRuleSet,AssociationRule

class NETCARIO:
	"""Class for IO on NETCAR files."""
	def __init__(self):
		"""Initialize the user-friendly feature to integer index maps."""
		self.feature_to_index = {}
		self.index_to_feature = []
	
	def load_map(self,filename):
		"""Load a map file containing one feature per line, and the line number is the index."""
		self.feature_to_index = {}
		self.index_to_feature = []
		data = open(filename).readlines()
		ln = 0
		for line in data:
			item = line.strip()
			self.index_to_feature.append(item)
			self.feature_to_index[item] = ln
			ln += 1
		

	def load_rules(self,filename,target_label="YES",merge_with_rules=None):
		"""Parse the NETCAR output into a new AssociationRuleSet."""
		data = open(filename).readlines()
		arset = None
		if merge_with_rules == None:
			arset = AssociationRuleSet()
			arset.rules = []
		else:
			arset = merge_with_rules
		header = [x.strip() for x in data[1][2:].split("\t")] # we implicitly assume the first field is the left side (comma sep), the second the right side (comma sep)
		arset.attributes = header[1:]
		for line in data[2:]:	# there should two header lines
			fields = [x.strip() for x in line.split()]
			items = tuple([self.index_to_feature[int(x.strip())] for x in fields[0].split(",")])
			label = target_label
			scores = [x.strip() for x in fields[1:]]
			attributes = {}
			for i in range(len(arset.attributes)):
				attributes[arset.attributes[i]] = scores[i]
			arset.rules.append(AssociationRule(items,[label],attributes))
		return arset

	def save(self,sample_set,netcar_filename):
		"""Save a sample set in NETCAR input format."""
		output_features_map_filename = "%s.features.map"%(netcar_filename)
		output_instance_map_filename = "%s.instances.map"%(netcar_filename)
		
		finstances = open(output_instance_map_filename,"w")
		for sample in sample_set:
			finstances.write("%s\n"%(sample.id))
		finstances.close()
		
		ffeatures = open(output_features_map_filename,"w")
		for feature in sample_set.index_to_feature:
			ffeatures.write("%s\n"%(feature))
		ffeatures.close()
		
		output_genotype_filename = "%s.genotype"%(netcar_filename)
		fgenotype = open(output_genotype_filename,"w")
		phenotype_map = {"YES":1,"NO":0,"NULL":-2}
		attribute_matrix = {}
		
		for sample in sample_set:
			attribute_matrix[sample.id] = sample._attributes_matrix
		for i in range(sample_set.get_number_of_features()):
			lineout = []
			fgenotype.write("%d"%(attribute_matrix[sample_set[0].id][i]))
			for sample in sample_set[1:]:
				lineout.append(attribute_matrix[sample.id][i])
			for x in lineout:
				fgenotype.write(" %d"%(x))
			fgenotype.write("\n")
		fgenotype.close()
		class_label_list = sample_set.class_label_set.get_classes()
		for c in class_label_list:
			phenotype_filename = "%s.%s.phenotype"%(netcar_filename,c)
			fphenotype = open(phenotype_filename,"w")
			lineout = []
			for sample in sample_set:
				print sample.id
				print sample.class_labels.keys()
				class_label = sample.get_class_label(c)
				lineout.append(str(phenotype_map[class_label]))
			fphenotype.write(",".join(lineout))
			fphenotype.close()
		