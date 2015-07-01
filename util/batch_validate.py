"""
Perform a comparison between feature selection methods of mutual information, conditionally weighted mutual information, 
conditional mutual information, and half mutual information half conditionally weighted mutual information.  The training and
testing on the dataset is done by LIBSVM.

@author Norman MacDonald
@date 2010-02-16
"""
import os,sys
from optparse import OptionParser, OptionGroup
from pica.Sample import SampleSet, ClassLabelSet
from pica.io.FileIO import FileIO
from pica.AssociationRule import load_rules
from pica.CrossValidation import CrossValidation
from pica.featureselectors.cwmi.CWMIRankFeatureSelector import CWMIRankFeatureSelector
from pica.trainers.libsvm.libSVMTrainer import libSVMTrainer
from pica.classifiers.libsvm.libSVMClassifier import libSVMClassifier
from pica.TestConfiguration import TestConfiguration
if __name__ == "__main__":
	parser = OptionParser(version="%prog 0.8")
	parser.add_option("-r","--replicates",type="int",help="Number of replicates [default = %default]",default=10)
	parser.add_option("-v","--folds",type="int",help="v-fold cross-validation [default = %default]",default=5)
	parser.add_option("-s","--samples",action="store",dest="input_samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-c","--classes",action="store",dest="input_classes_filename",help="Read class labels from FILE",metavar="FILE")
	parser.add_option("-t","--targetclass",action="store",dest="target_class",help="Set the target CLASS for testing",metavar="CLASS")
	parser.add_option("-o","--output_filename",help="Write results to FILE",metavar="FILE",default=None)
	parser.add_option("-p","--parameters",action="store",dest="parameters",help="FILE with additional, classifier-specific parameters. (confounders for CWMI)",metavar="FILE",default=None)
	parser.add_option("-z","--confounder",help="Name of confounder to use (e.g. the taxonomic level) [default: %default]",default="order")
	parser.add_option("-f","--features_per_class",type="int",help="Number of features per class label [default: %default]",default=2)
	parser.add_option("-d","--metadata",help="Load metadata from FILE and add to misclassification report [default: %default]",metavar="FILE",default=None)
	
	(options, args) = parser.parse_args()

		
	fileio = FileIO()
	samples = fileio.load_samples(options.input_samples_filename)
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
	
	test_configurations = []
	confounders = ("genus","family","order","class","phylum","superkingdom")
	scores_list = (("cmi",),("cwmi",),("mi","cwmi"))
	
	feature_selector = CWMIRankFeatureSelector(confounders_filename=options.parameters,scores=("mi",),features_per_class=options.features_per_class,confounder=options.confounder)
	trainer = libSVMTrainer(kernel_type="LINEAR",C=5)
	classifier = libSVMClassifier()
	tc = TestConfiguration("mi",feature_selector,trainer,classifier)
	test_configurations.append(tc)
	

	for scores in scores_list:
		feature_selector = CWMIRankFeatureSelector(features_per_class=options.features_per_class,confounder=options.confounder,scores=scores,confounders_filename=options.parameters)
		tc = TestConfiguration("%s_%s"%("_".join(scores),options.confounder),feature_selector,trainer,classifier)
		test_configurations.append(tc)

	root = "%s_%s_p%dn%d"%(options.target_class,options.confounder,options.features_per_class,options.features_per_class)
	
	crossvalidator = CrossValidation(samples,options.parameters,options.folds,options.replicates,test_configurations,root_output=options.output_filename)
	crossvalidator.crossvalidate()
	