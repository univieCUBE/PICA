"""
Test the association rule model on a sample set.

@author Norman MacDonald
@date 2010-02-16
"""
import os,sys
from optparse import OptionParser
from pica.io.FileIO import FileIO, error
from pica.AssociationRule import load_rules
from libsvm290.python.svm import svm_model #RVF
import pickle # RVF
	

if __name__ == "__main__":
	parser = OptionParser(version="PICA %prog 1.0.1")
	parser.add_option("-s","--samples",action="store",dest="input_samples_filename",help="Read samples from FILE",metavar="FILE")
	parser.add_option("-c","--classes",action="store",dest="input_classes_filename",help="Read class labels from FILE",metavar="FILE")
	parser.add_option("-m","--model_filename",action="store",help="use model from FILE for classification",metavar="FILE")
	parser.add_option("-z","--model_accuracy",action="store",help="use model accuracy for classification",metavar="FILE",default="laplace")
	parser.add_option("-t","--targetclass",action="store",dest="target_class",help="Set the target CLASS for testing",metavar="CLASS")
	parser.add_option("-a","--algorithm",action="store",dest="algorithm",help="The algorithm for testing",metavar="ALG", default="libsvm.libSVMClassifier" )
	parser.add_option("-p","--parameters",action="store",dest="parameters",help="FILE with additional, classifier-specific parameters.",metavar="FILE",default=None)
	(options, args) = parser.parse_args()
	
	# Check arguments for crucial errors
	errorCount = 0
	if not options.input_samples_filename:
		error("Please provide a genotype sample file with -s /path/to/genotype.file")
		errorCount += 1
	if not options.model_filename:
		error("Please provide a model file for this phenotype with -m /path/to/model.file")
		errorCount += 1
	if not options.target_class:
		error("Please provide the phenotype target to be predicted with -t \"TRAITNAME\"")
		errorCount += 1
	if errorCount > 0:
		error("For help on usage, try calling:\n\tpython %s -h" % os.path.basename(sys.argv[0]))
		exit(1)
	
	fileio = FileIO()
	if options.algorithm == "libsvm.libSVMClassifier": # RVF: part of SVM fix (feature-index map)
		samples = fileio.load_samples(options.input_samples_filename, indexToAttribute=options.model_filename)
	else: #original code
		samples = fileio.load_samples(options.input_samples_filename)
	if options.input_classes_filename:
		classes = fileio.load_classes(options.input_classes_filename)
	else:
		classes = fileio.init_null_classes(options.input_samples_filename, options.target_class)
	
	#RVF
	"""rules = load_rules(options.model_filename) #original code"""
	if options.algorithm == "libsvm.libSVMClassifier":
		m = svm_model(options.model_filename)
		with open(options.model_filename+".classlabelmap", 'rb') as handle:
			clm = pickle.loads(handle.read())
		with open(options.model_filename+".classlabelmapindex", 'rb') as handle:
			clmi= pickle.loads(handle.read())
		rules = {"svm_model":m,"class_label_map":clm,"class_label_map_index":clmi}
	else: #i.e. options.algorithm == "cpar.CPARClassifier":
		rules = load_rules(options.model_filename)
	#/RVF
	samples.load_class_labels(classes)
	samples.set_current_class(options.target_class)
	if options.input_classes_filename: 
		samples.hide_nulls(options.target_class)
	modulepath = "pica.classifiers.%s"%(options.algorithm)
	classname = options.algorithm.split(".")[-1]
	ClassifierClass = __import__(modulepath, fromlist=(classname,))

	#RVF. Original code is in the ELSE statement	
	if options.algorithm == "libsvm.libSVMClassifier":
		classifier = ClassifierClass.__dict__[classname]()
	else:
		classifier = ClassifierClass.__dict__[classname](accuracy_measure=options.model_accuracy)
	#/RVF
	
	classifier.set_null_flag("NULL")
	classification_results = classifier.test(samples,rules)
	
	if options.input_classes_filename:
		print classification_results.print_classification_log()
		print classification_results
	else:
		classification_results.print_classification_log_predictedOnly()
