"""
Given a sampleset, sample identifier and rule set, output the rules that apply to the sample.

@author Norman MacDonald
@date 2010-03-12
"""
import os,sys
from optparse import OptionParser, OptionGroup
from pica.Sample import SampleSet, ClassLabelSet
from pica.io.FileIO import FileIO
from pica.AssociationRule import load_rules
from pica.utils.ProgramTimer import ProgramTimer
from pica.AssociationRule import load_rules,AssociationRuleSet

def is_equal(ruleseta,rulesetb):
	keyedset = {}
	equals = True
	for itema in ruleseta:
		keyedset[(tuple(itema.ls),tuple(itema.rs))] = 1
	for itemb in rulesetb:
		if not keyedset.has_key((tuple(itemb.ls),tuple(itemb.rs))):
			equals = False
	return equals
		

def get_same_rulesets(sample_rulesets):
	seta = {}
	for keya in sample_rulesets.keys():
		if not seta.has_key(keya):
			seta[keya] = [keya]
			for keyb in sample_rulesets.keys():
				if not seta.has_key(keyb):
					equality = is_equal(sample_rulesets[keya],sample_rulesets[keyb])
					if equality:
						seta[keya].append(keyb)
						seta[keyb] = [keya]
	return seta


if __name__ == "__main__":
	pt = ProgramTimer()
	parser = OptionParser(version="%prog 0.8")
	parser.add_option("-s","--samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-m","--model_filename",help="Read rules from FILE",metavar="FILE")
	parser.add_option("-o","--output_filename",help="Write selected organisms to FILE",metavar="FILE")
	parser.add_option("-c","--classes_filename",help="Read class labels from FILE",metavar="FILE")
	parser.add_option("-t","--target_class",help="Target class.",metavar="CLASS")
	
	(options, args) = parser.parse_args()

	
	pt.start()
	fileio = FileIO()
	samples = fileio.load_samples(options.samples_filename)
	classes = fileio.load_classes(options.classes_filename)
	samples.load_class_labels(classes)
	samples.set_current_class(options.target_class)
	target_samples = []
	samples_time = pt.stop()
	print "Loaded samples (%0.2fs)"%(samples_time)
	
	pt.start()
	
	rules = load_rules(options.model_filename)
	indexed_rules = rules.remap_feature_to_index(samples)
	training_time = pt.stop()
	newsamples = {}
	
	for sample in samples:
		keep_sample = False
		for rule in indexed_rules:
			if sample.satisfies(rule.ls):
				if not newsamples.has_key(sample.id):
					newsamples[sample.id] = []
				newsamples[sample.id].append(rule)
	sets = get_same_rulesets(newsamples)
	
	finished = {}
	f = open(options.output_filename,"w")
	for sampleid in newsamples.keys():
		if not finished.has_key(sampleid):
			finished[sampleid] = 1
		if len(sets[sampleid]) == 1 and sets[sampleid][0] != sampleid:
			continue
		sample_id_list = []
		class_label_counts = {}
		for sid in sets[sampleid]:
			class_label = samples.get_by_id(sid).get_class_label()
			if not class_label_counts.has_key(class_label):
				class_label_counts[class_label] = 0
			class_label_counts[class_label] += 1
			sample_id_list.append("%s(%s)"%(sid,class_label))
		for class_label in sorted(class_label_counts.keys()):
			f.write("%s:%d  "%(class_label,class_label_counts[class_label]))
		f.write("%s\n"%(",".join(sample_id_list)))
		
		sample_rules = []
		arset = AssociationRuleSet()
		arset.extend(newsamples[sampleid])
		arset = arset.remap_index_to_feature(samples)
		for rule in arset:
			sample_rules.append("((%s)>(%s)(%s))"%(",".join(rule.ls),",".join(rule.rs),rule.attributes["laplace"]))
		f.write("\n".join(sample_rules))
		f.write("\n\n")
	
	"Do aggregate analysis of broken down rules"
	finished_items = {}
	for rule in indexed_rules:
		for item in rule.ls:
			finished_items[item] = 1
	items = sorted(finished_items.keys())
	f.write("\n\nItems in rules\n\n")
	all_class_labels = {}
	for sample in samples:
		all_class_labels[sample.get_class_label()] = 1
	all_class_labels = sorted(all_class_labels.keys())
	f.write("Item\t%s\n"%("\t".join(all_class_labels)))
	for item in items:
		class_label_counts = {}
		for sample in samples:
			class_label = sample.get_class_label()
			if sample.satisfies((item,)):
				if not class_label_counts.has_key(class_label):
					class_label_counts[class_label]=0
				class_label_counts[class_label] += 1
		class_label_counts_list = ["%d"%(class_label_counts[x]) for x in all_class_labels]
		f.write("%s\t%s\n"%(samples.index_to_feature[item],"\t".join(class_label_counts_list)))
		
	f.close()
	