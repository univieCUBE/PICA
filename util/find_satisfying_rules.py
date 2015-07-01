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




if __name__ == "__main__":
	pt = ProgramTimer()
	parser = OptionParser(version="%prog 0.8")
	parser.add_option("-s","--samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-m","--model_filename",help="Read rules from FILE",metavar="FILE")
	parser.add_option("-t","--target_sample",help="Set the target SAMPLE for selecting",metavar="SAMPLE")
	parser.add_option("-f","--target_samples_filename",help="Read target samples from filename, one per line")
	parser.add_option("-o","--output_filename",help="Write selected rules to FILE",metavar="FILE")
	parser.add_option("-g","--output_genomes",action="store_true",default=False,help="Output genomes that satisfy rules instead")
	
	(options, args) = parser.parse_args()

	
	pt.start()
	fileio = FileIO()
	samples = fileio.load_samples(options.samples_filename)
	target_samples = []
	if options.target_sample:
		for sample in samples:
			if (sample.id == options.target_sample):
				target_samples.append(sample)
	elif options.target_samples_filename:
		target_sample_ids = [x.strip() for x in open(options.target_samples_filename).readlines()]
		for target_sample_id in target_sample_ids:
			for sample in samples:
				if (sample.id == target_sample_id):
					target_samples.append(sample)
	else:
		print "You must specify a target sample"
		sys.exit(1)
	
	if len(target_samples) ==0:
		print "Could not find samples!"
		sys.exit()
	samples_time = pt.stop()
	print "Loaded samples (%0.2fs)"%(samples_time)
	
	pt.start()
	
	rules = load_rules(options.model_filename)
	rules = rules.remap_feature_to_index(samples)
	training_time = pt.stop()
	newrules = []
	
	for rule in rules:
		keep_rule = False
		for target_sample in target_samples:
			if target_sample.satisfies(rule.ls):
				keep_rule = True
		if keep_rule:
			newrules.append(rule)
	newruleset = AssociationRuleSet()
	newruleset.extend(newrules)
	newruleset = newruleset.remap_index_to_feature(samples)
	newruleset.write(filename=options.output_filename)
	
	
	
	
	