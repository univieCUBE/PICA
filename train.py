"""
Train a classifier with a sample set.

@author Norman MacDonald
@date 2010-02-16
"""
import os,sys
from optparse import OptionParser
from pica.io.FileIO import FileIO
from pica.utils.ProgramTimer import ProgramTimer
from pica.io.FileIO import error
import pickle # RVF



if __name__ == "__main__":
	pt = ProgramTimer()
	parser = OptionParser(version="PICA %prog 1.0.1")
	parser.add_option("-a","--algorithm",action="store",dest="algorithm",
					help="Training algorithm [default = %default]",metavar="ALG",default="libsvm.libSVMTrainer")
	parser.add_option("-k","--svm_cost",action="store",dest="C",metavar="FLOAT",help="Set the SVM misclassification penalty parameter C to FLOAT")
	parser.add_option("-s","--samples",action="store",dest="input_samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-c","--classes",action="store",dest="input_classes_filename",help="Read class labels from FILE",metavar="FILE")
	parser.add_option("-t","--targetclass",action="store",dest="target_class",help="Set the target CLASS for testing",metavar="CLASS")
	parser.add_option("-o","--output",action="store",dest="output_filename",help="Write rules to FILE",metavar="FILE",default=None)
	parser.add_option("-p","--parameters",action="store",dest="parameters",help="FILE with additional, classifier-specific parameters. (confounders for CWMI)",metavar="FILE",default="taxonomic_confounders.txt")
	parser.add_option("-f","--feature_select",help="Model file (currently only association rule files) with features to select from [default: %default]",metavar="FILE",default=None)
	parser.add_option("-1","--feature_select_score",help="Order features by (feature selection option)", default="order_cwmi")
	parser.add_option("-n","--feature_select_top_n",help="Take the top n features(feature selection option)", type="int", default=20)

	(options, args) = parser.parse_args()

	# Check arguments for crucial errors
	errorCount = 0
	if not options.input_samples_filename:
		error("Please provide a genotype sample file with -s /path/to/genotype.file")
		errorCount += 1
	if not options.input_classes_filename:
		error("Please provide a phenotype class file with -c /path/to/phenotype.file")
		errorCount += 1
	if not options.target_class:
		error("Please provide the phenotype target to be predicted with -t \"TRAITNAME\"")
		errorCount += 1
	if errorCount > 0:
		error("For help on usage, try calling:\n\tpython %s -h" % os.path.basename(sys.argv[0]))
		exit(1)
	
	pt.start()
	fileio = FileIO()
	samples = fileio.load_samples(options.input_samples_filename)
	samples_time = pt.stop()
	print "Loaded samples (%0.2fs)"%(samples_time)
	if options.feature_select:
		print "Selecting top %d features from %s, ordered by %s"%(options.feature_select_top_n,options.feature_select,options.feature_select_score)
		pt.start()
		from pica.AssociationRule import load_rules,AssociationRuleSet
		selected_rules = AssociationRuleSet()
		rules = load_rules(options.feature_select)
		rules.set_target_accuracy(options.feature_select_score)
		selected_rules.extend(rules[:options.feature_select_top_n])
		samples = samples.feature_select(selected_rules)
		print "Finished feature selection (%0.2fs)"%(pt.stop())
	classes = fileio.load_classes(options.input_classes_filename)
	samples.load_class_labels(classes)
	print samples.get_number_of_features()
	samples.set_current_class(options.target_class)
	
	pt.start()
	print "Compressing features...",
	samples = samples.compress_features()
	compression_time = pt.stop()
	print "\bfinished compression.(%0.2fs)"%(compression_time)
	samples.set_current_class(options.target_class)
	
	
	samples.hide_nulls(options.target_class)
	
	modulepath = "pica.trainers.%s"%(options.algorithm)
	classname = options.algorithm.split(".")[-1]
	TrainerClass = __import__(modulepath, fromlist=(classname,))
	if options.C:
		trainer = TrainerClass.__dict__[classname](options.parameters, C=options.C, probability = 1)
	else:
		trainer = TrainerClass.__dict__[classname](options.parameters)
	
	trainer.set_null_flag("NULL")
	pt.start()
	print "Starting training algorithm"
	rules = trainer.train(samples)
	training_time = pt.stop()
	if options.output_filename == None:
		options.output_filename = "%s.rules"%(options.target_class)
	""" Original code. Changes by RVF: see below.
	rules.write(filename=options.output_filename)
	"""
	# RVF
	if hasattr(rules, "write"):
		# i.e. CPAR
		rules.write(filename=options.output_filename)
	else:
		# i.e. CPAR2SVM or SVM
		# creating 4 files. NOTE the hardcoded extensions
		# Export the SVM model, using libSVM save method
		rules['svm_model'].save(filename=options.output_filename)
		# Export class label map and the index (i.e. which class id corresponds to presence/absence)
		with open(options.output_filename+".classlabelmap",'w') as outfile:
			pickle.dump(rules["class_label_map"],outfile) #fails with model, because of SWIGpy object
		# TODO: I/O only one of these two, since they hold the same data in principle
		with open(options.output_filename+".classlabelmapindex",'w') as outfile:
			pickle.dump(rules["class_label_map_index"],outfile)
		# Export the feature map (i.e. which COG corresponds to which SVM model dimension)
		with open(options.output_filename+".featuremapindex",'w') as outfile:
			pickle.dump(samples.get_index_to_feature(), outfile)
			
	"""	#Ugly hack to directly test the rules
		classifier = libSVMClassifier()
		fileio = FileIO()
		testset = fileio.load_samples(options.output_filename)
		results = classifier.test(testset,rules)
		print results
		pprint.pprint(results)
	"""
	"""	with open(options.output_filename,'w') as outfile:
			model = pprint.pformat(rules,indent=2)
			outfile.write(model)
			rules['svm_model'].save(filename=outfile)
	"""
	# /RVF
	
	print "Finished training. (%0.2fs)"%(training_time)
	total_time = pt.end()
	print "Model output to %s. Total time: (%0.2fs)"%(options.output_filename,total_time)
	
	
