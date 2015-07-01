"""
Data structure for association rules.

@author Norman MacDonald
@date 2010-02-16
"""

import sys
from copy import deepcopy

class AssociationRule():
	"""Association rule data structure"""
	def __init__(self, ls=[], rs=[], attributes={}):
		"""Initialize a new association rule."""
		self.ls = ls
		self.rs = rs
		self.attributes = attributes
		self.accuracy = 0
	
	def __getitem__(self,instance):
		"""Return the attribute or None."""
		return self.attributes.get(instance,None)
		
	def __setitem__(self,key,value):
		"""Set an attribute for this rule."""
		self.attributes[key] = value
		
	def keys(self):
		"""Return an unordered list of attributes for this rule."""
		return self.attributes.keys()
		
	def __delitem__(self,key):
		"""Delete an attribute from this rule."""
		del self.attributes[key]
	
	def __cmp__(self,other):
		"""Compare rules by the accuracy field."""
		if other == None: return -1
		if self.accuracy < other.accuracy:
			return 1
		if self.accuracy == other.accuracy:
			return 0
		return -1
	def __str__(self):
		"""Return the antecedent and consequent of this rule."""
		return "%s\t%s"%(self.ls,self.rs)

class AssociationRuleSet():
	"""Data structure for a set of association rules."""
	
	def __init__(self):
		"""Initialize an empty set of associatino rules."""
		self.attributes = []
		self.rules = []
		self.field_sep = "\t"
		self.rule_sep = ","
		self.null_flag = "NULL"
		self.target_accuracy = "laplace"

	def _update_attribute_list(self):
		"""Cycle through all rules and update the master list of attributes.
		
		It is possible to add a new attribute to a rule without updating the set.
		Here we update the main list of attributes with any new attributes.
		This is important for preserving the ordering of the output tab delimited file.
		"""
		for rule in self.rules:
			for key in rule.attributes.keys():
				if key not in self.attributes:
					self.attributes.append(key)
	def __getitem__(self,index):
		"""Return the rule at index."""
		return self.rules[index]
		
	def __iter__(self):
		"""Return an iterator to the rules."""
		return self.rules.__iter__()
	
	def load(self,filename):
		"""
		Load rules from a tab delimited text file.
		
		The antecedent and consequent should be in the first two columns, respectively.  If either
		contains more than one item, they should be comma separated within the tab separated column.  
		All other columns will be loaded as an attribute for the rule (e.g. laplace accuracy, mi)
		"""
		data = open(filename).readlines()
		self.rules = []
		header = [x.strip() for x in data[0].split("\t")] #we implicitly assume the first field is the left side (comma sep), the second the right side (comma sep)
		self.attributes = header[2:]
		for line in data[1:]:	#there should be a header
			fields = [x.strip() for x in line.split("\t")]
			items = tuple([x.strip() for x in fields[0].split(",")])
			label = fields[1].strip()
			scores = [x.strip() for x in fields[2:]]
			attributes = {}
			for i in range(len(self.attributes)):
				attributes[self.attributes[i]] = scores[i]
			self.rules.append(AssociationRule(items,[label],attributes))
		self.set_target_accuracy("laplace")
		
	def write(self,filename):
		"""Write the rules to a tab-delimited text file.
		
		The first two columns will be comma separated antecedent and consequent of the rule, followed
		by each metadata value.  The order of the attributes of set of rules read into this data structure 
		is preserved.  Before writing begins, the rule list is cycled through for any new attributes appended
		to a rule, and each each added to the end of the columns.
		"""
		#run through all rules and add any new attributes to the end of the list
		self._update_attribute_list()
		fout = open(filename,"w")
		fout.write("antecedent%sconsequent%s%s\n"%(self.field_sep,self.field_sep,self.field_sep.join(self.attributes)))
		for rule in self.rules:
			fout.write("%s%s%s"%(self.rule_sep.join(rule.ls),self.field_sep,self.rule_sep.join(rule.rs)))
			for attribute in self.attributes:
				attvalue = rule[attribute]
				if attvalue == None:
					attvalue = self.null_flag
				fout.write("%s%s"%(self.field_sep,attvalue))
			fout.write("\n")
		fout.close()
		
	def __len__(self):
		"""Return the number of rules in this set."""
		return len(self.rules)

	def remap_index_to_feature(self,sample_set):
		"""Map the integer antecedent to the user-friendly feature string and return a new AssociationRuleSet."""
		association_rule_set = AssociationRuleSet()
		for rule in self:
			ls = rule.ls
			#for item in rule.ls:
			#	ls.extend([x.strip() for x in item.split("/")])
			ls = map(lambda i: sample_set.index_to_feature[i],ls)
			association_rule_set.rules.append(AssociationRule(ls,rule.rs,rule.attributes))
		association_rule_set.set_target_accuracy(self.target_accuracy)
		
		return association_rule_set
		
	def remap_feature_to_index(self,sample_set):
		"""Map the user-friendly antecedent to the efficient integer and return a new AssociationRuleSet."""
		association_rule_set = AssociationRuleSet()
		for rule in self:
			ls = rule.ls
			ls = map(lambda i: sample_set.feature_to_index.get(i,-2),ls)
			association_rule_set.rules.append(AssociationRule(ls,rule.rs,rule.attributes))
		association_rule_set.set_target_accuracy(self.target_accuracy)
		return association_rule_set
		
	
	def extend(self,association_rule_list):
		"""Extend this set with a list of association rules.
		
		This will also update the attribute list."""
		self.rules.extend(association_rule_list)
		self._update_attribute_list()

	
	def set_target_accuracy(self,target_accuracy):
		"""Set the accuracy of each rule to a given attribute.
		
		Once the accuracy has been set to a numeric attribute, the ruleset is sorted in
		descending order based on that accuracy.  Classifiers are expected to use the 
		loaded accuracy for evaluation."""
		
		self.target_accuracy = target_accuracy
		for rule in self:
			rule.accuracy = float(rule.attributes.get(target_accuracy,0))
		self.rules.sort()
		
			
def load_rules(rules_filename):
	"""Create a new AssociationRuleSet from a file."""
	association_rule_set = AssociationRuleSet()
	association_rule_set.load(filename=rules_filename)
	return association_rule_set
	
def save_rules(association_rule_set, filename):
	"""Save the association_rule_set to a given tab delimited file."""
	association_rule_set.write(filename=filename)
