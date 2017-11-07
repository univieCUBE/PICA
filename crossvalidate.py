#!/usr/bin/env python
"""
Perform cross-validation with a given training algorithm and classification algorithm

@author Norman MacDonald
@date 2010-02-16
"""
import os,sys
from optparse import OptionParser
from pica.io.FileIO import FileIO
from pica.CrossValidation import CrossValidation
from pica.TestConfiguration import TestConfiguration
from pica.io.FileIO import error
from pprint import pprint # add by RVF

if __name__ == "__main__":
	parser = OptionParser(version="PICA %prog 1.0.1")
	parser.add_option("-a","--training_algorithm",help="Training algorithm [default = %default]",metavar="ALG",default="libsvm.libSVMTrainer")
	parser.add_option("-k","--svm_cost",action="store",dest="C",metavar="FLOAT",help="Set the SVM misclassification penalty parameter C to FLOAT")
	parser.add_option("-b","--classification_algorithm",help="Testing algorithm [default = %default]",metavar="ALG",default="libsvm.libSVMClassifier")
	parser.add_option("-m","--accuracy_measure",help="Accuracy measure [default = %default]",metavar="ALG",default="laplace")
	parser.add_option("-r","--replicates",type="int",help="Number of replicates [default = %default]",default=10)
	parser.add_option("-v","--folds",type="int",help="v-fold cross-validation [default = %default]",default=5)
	parser.add_option("-s","--samples",action="store",dest="input_samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-c","--classes",action="store",dest="input_classes_filename",help="Read class labels from FILE",metavar="FILE")
	parser.add_option("-t","--targetclass",action="store",dest="target_class",help="Set the target CLASS for testing",metavar="CLASS")
	parser.add_option("-o","--output_filename",help="Write results to FILE",metavar="FILE",default=None)
	parser.add_option("-p","--parameters",action="store",dest="parameters",help="FILE with additional, classifier-specific parameters. (confounders for CWMI)",metavar="FILE",default=None)
	parser.add_option("-x","--profile",action="store_true",dest="profile",help="Profile the code",default=False)
	# RVF add option save crossval files
	parser.add_option("-y","--save_crossval_files",action="store_true",dest="crossval_files",help="Save the training and test sets for crossvalidation to files under /crossvalidation",default=False)

	parser.add_option("-d","--metadata",help="Load metadata from FILE and add to misclassification report [default: %default]",metavar="FILE",default=None)
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
	if not options.output_filename:
		error("Please specify a file for the output with -o /path/to/result.file")
		errorCount += 1
	if errorCount > 0:
		error("For help on usage, try calling:\n\tpython %s -h" % os.path.basename(sys.argv[0]))
		exit(1)
		
	fileio = FileIO()
	samples = fileio.load_samples(options.input_samples_filename)
	if options.feature_select:
		print "Selecting top %d features from %s, ordered by %s"%(options.feature_select_top_n,options.feature_select,options.feature_select_score)
		from pica.AssociationRule import load_rules,AssociationRuleSet
		selected_rules = AssociationRuleSet()
		rules = load_rules(options.feature_select)
		rules.set_target_accuracy(options.feature_select_score)
		selected_rules.extend(rules[:options.feature_select_top_n])
		samples = samples.feature_select(selected_rules)
	classes = fileio.load_classes(options.input_classes_filename)
	samples.load_class_labels(classes)
	print "Sample set has %d features."%(samples.get_number_of_features())
	samples.set_current_class(options.target_class)
	print "Parameters from %s"%(options.parameters)
	print "Compressing features...",
	samples = samples.compress_features()
	print "compressed to %d distinct features."%(samples.get_number_of_features())
	
	samples.set_current_class(options.target_class)
	samples.hide_nulls(options.target_class)
	
	
	modulepath = "pica.trainers.%s"%(options.training_algorithm)
	classname = options.training_algorithm.split(".")[-1]
	TrainerClass = __import__(modulepath, fromlist=(classname,))
	if options.C:
		trainer = TrainerClass.__dict__[classname](options.parameters, C=options.C)
	else:
		trainer = TrainerClass.__dict__[classname](options.parameters)
	trainer.set_null_flag("NULL")
	
	modulepath = "pica.classifiers.%s"%(options.classification_algorithm)
	classname = options.classification_algorithm.split(".")[-1]
	ClassifierClass = __import__(modulepath, fromlist=(classname,))
	classifier = ClassifierClass.__dict__[classname](options.parameters)
	classifier.set_null_flag("NULL")
	
	test_configurations = [TestConfiguration("A",None,trainer,classifier)]
	
	#RVF changed (added the last 3 parameters)
	if ( options.crossval_files ):
		crossvalidator = CrossValidation(samples,options.parameters,options.folds,options.replicates,test_configurations,False,None,options.target_class,options.output_filename)
	else:
		crossvalidator = CrossValidation(samples,options.parameters,options.folds,options.replicates,test_configurations)		
	crossvalidator.crossvalidate()
	classifications,misclassifications = crossvalidator.get_classification_vector()
	metadata = None
	if options.metadata:
		metadata = fileio.load_metadata(options.metadata)
	
	fout = open(options.output_filename,"w")
	fout.write("who\t%s\tFalse Classifications\tTrue Classifications\tTotal"%(options.target_class))
	if metadata:
		for key in metadata.get_key_list():
			fout.write("\t%s"%(key))
	fout.write("\n")
	for who in misclassifications.keys():
		fout.write("%s\t%s\t%d\t%d\t%d"%(who,classes[who][options.target_class],misclassifications[who][0],misclassifications[who][1],misclassifications[who][0]+misclassifications[who][1]))
		if metadata:
			m = metadata.get(who,{})
			for key in metadata.get_key_list():
				fout.write("\t%s"%(m.get(key,"")))
		fout.write("\n")
	stats = crossvalidator.get_summary_statistics(0)
	pprint(stats)
	fout.close()
