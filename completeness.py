"""
Perform cross-validation with a given training algorithm and classification algorithm

@author Norman MacDonald
@date 2010-02-16
"""
import os,sys
from optparse import OptionParser
from pica.io.FileIO import FileIO
from pica.Completeness import Completeness
#from pica.CrossValidation import CrossValidation
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

        # PH add option completeness, contamination
        parser.add_option("-w","--completeness",help="Completeness value between 0-1 (default = %default)",type="int",metavar="INT",default=2)
        parser.add_option("-z","--contamination",help="Contamination level between 0-1 (default = %default)",type="int",metavar="INT",default=2)
	
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
        unmodified_samples=fileio.load_samples(options.input_samples_filename)
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
        unmodified_samples.load_class_labels(classes)
	samples.load_class_labels(classes)
	print "Sample set has %d features."%(samples.get_number_of_features())
        unmodified_samples.set_current_class(options.target_class)
	samples.set_current_class(options.target_class)
	print "Parameters from %s"%(options.parameters)
	print "Compressing features...",

        #for the moment: don't compress features. potential bug with testing! potentially interferes with completeness check
        samples = samples.compress_features()

	print "compressed to %d distinct features."%(samples.get_number_of_features())
	
        unmodified_samples.hide_nulls(options.target_class)

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
        	crossvalidator = Completeness(samples,options.parameters,options.folds,options.replicates,options.completeness,options.contamination,test_configurations,unmodified_samples,False,None,options.target_class,options.output_filename)
	else:
		crossvalidator = Completeness(samples,options.parameters,options.folds,options.replicates,options.completeness,options.contamination,test_configurations,unmodified_samples)		
	crossvalidator.crossvalidate()

        #contamination makes this kind of output quite difficult. so leaving out at the moment

	fout = open(options.output_filename,"w")
	
        stats = crossvalidator.get_summary_statistics(0)
        resorted={}
        for index in stats[0][0].keys():
            resorted[index]=[]
            for w in range(len(stats)):
                resorted[index].append([])
                for z in range(len(stats[w])):
                    resorted[index][w].append(stats[w][z][index])


        for index in resorted.keys():
            fout.write("[%s]\n"%index)
            for w in range(len(resorted[index])):
                printline=[]
                for z in range(len(resorted[index][w])):
                    printline.append(str(resorted[index][w][z]))
                fout.write("%s\n"%"\t".join(printline))
            fout.write("\n")

	#pprint(stats)
	fout.close()
