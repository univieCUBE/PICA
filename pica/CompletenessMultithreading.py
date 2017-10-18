"""
Take a set of samples and labels, randomly sort and V-fold cross-validate R times with Z completeness and W contamination

@author: Norman MacDonald
@date: 2010-02-19

"""
from ClassificationResults import ClassificationResults, ClassificationSummary
from math import sqrt

from pica.io.FileIO import FileIO
from pica.Sample import SampleSet
import time
import os
import pickle

import sys
MPI_PARALLEL = False

#from multiprocessing import Process
import multiprocessing

#class Completeness():
#        """The main completeness-assay class."""
def replicateProcess(parametertuple):
            training_set, test_set, dataset, replicate, fold = parametertuple
            output=[]
            replicate_plus_one=replicate+1
            print "Fold %d: training_set: %d, test set: %d"%(fold,len(training_set),len(test_set))
            if ( dataset.target_class != None ):
                fileio = FileIO()
                trainingSetFile = outputPath+"/"+str(dataset.target_class)+"_R"+str(replicate)+"_F"+str(fold)+"_training.set"
                testSetFile =     outputPath+"/"+str(dataset.target_class)+"_R"+str(replicate)+"_F"+str(fold)+"_test.set"
                print "Saving training set to: "+trainingSetFile
                fileio.save_samples(training_set,trainingSetFile)
                print "Saving test set to: "+testSetFile
                fileio.save_samples(test_set,testSetFile)

            for test_configuration_index in xrange(len(dataset.test_configurations)):
                test_configuration=dataset.test_configurations[test_configuration_index]
                test_name = test_configuration.name
                new_training_set = training_set
                new_test_set = test_set
                if test_configuration.feature_selector:
                    features = test_configuration.feature_selector.select(training_set)
                    new_training_set = training_set.feature_select(features)
                    new_test_set = test_set.feature_select(features)
                model = test_configuration.trainer.train(new_training_set)

                if dataset.outputFilename != None:
                    if not hasattr(model, 'write'): # i.e. probably SVM model
                        svmModelFile = outputPath+"/"+str(dataset.target_class)+"_R"+str(replicate)+"_F"+str(fold)+"_svm.model"                                                   
                        model['svm_model'].save(filename=svmModelFile)
                        with open(svmModelFile+".classlabelmap",'a') as outfile:
                            pickle.dump(model["class_label_map"],outfile) #fails with model, because of SWIGpy object
                        with open(svmModelFile+".classlabelmapindex",'a') as outfile:
                            pickle.dump(model["class_label_map_index"],outfile)
                        with open(svmModelFile+".featuremapindex",'w') as outfile:
                            pickle.dump(new_training_set.get_index_to_feature(), outfile)


                all_class_labels=new_test_set.get_class_labels()
                sample_attribute_collection={}
                for index in all_class_labels:
                    sample_attribute_collection[index]=[]

                for sample in new_test_set.__iter__():
                    temp_attributes_list=list(sample.get_attributes_index_list())
                    sample_attribute_collection[sample.current_class_label].append(temp_attributes_list)



                for w in xrange(dataset.w):
                    output.append([])
                    incomplete_test_set = new_test_set.induce_incompleteness(dataset.completeness[w])
                    err=0
                    for z in xrange(dataset.z):
                        #output[w][z].append([])
                        if round(dataset.contamination[z],1) == 0.0:
                            results = test_configuration.classifier.test(incomplete_test_set.map_test_set_attributes_to_training_set(new_training_set),model)
                            summary = ClassificationSummary(results)
                            output[w].append(summary)

                        elif len(sample_attribute_collection.keys())==2:
                            #do crosscontamination if exactly 2 class labels given
                            contaminated_test_set = incomplete_test_set.introduce_contamination(sample_attribute_collection,dataset.contamination[z])

                            contaminated_test_set = contaminated_test_set.map_test_set_attributes_to_training_set(new_training_set)
                              
                            results = test_configuration.classifier.test(contaminated_test_set,model)
                            summary = ClassificationSummary(results)
                            output[w].append(summary)

                            if ( dataset.target_class != None ):
                                print results.print_classification_log()
                                print results

                            if dataset.root_output:
                                fout = open("%(dataset.root_output)s.r%(replicate_plus_one)d.v%(fold)d.%(test_name)s.features"%(locals()),"w")
                                fout.write("\n".join(features))
                                fout.close()
                        elif err==0:
                            sys.stderr.write("Warning: skipping contamination of fold %i of replicate %i: exactly 2 different class labels needed!"%(fold,replicate))
                            err=1

                        #print(dataset.replicates[replicate][fold][w][z])
                                
#            if dataset.root_output:

#                fout = open("%(dataset.root_output)s.r%(replicate_plus_one)d.classification.log"%(locals()),"w")
#                header_fields = ["sample","fold",dataset.sample_set.current_class]
#                for test_configuration in dataset.test_configurations:
#                      header_fields.append(test_configuration.name)
#                output_dictionary = {}
#                output_lines = ["\t".join(header_fields)]
#                for fold in xrange(dataset.v):
#                      for classification_index in xrange(len(dataset.replicates[replicate][fold][0].classifications_list)):
#                              main_sample_record = dataset.replicates[replicate][fold][0].classifications_list[classification_index]
#                              output_line = [str(main_sample_record.who),str(fold+1),str(main_sample_record.true_class)]
#                              for test_configuration_index in xrange(len(dataset.test_configurations)):
#                                      test_sample_record = dataset.replicates[replicate][fold][test_configuration_index].classifications_list[classification_index]
#                                      output_line.append(str(test_sample_record.predicted_class))
#                              output_lines.append("\t".join(output_line))
#                fout.write("\n".join(output_lines))
#                fout.close()
            print "Finished replicate %d, fold %d"%(replicate_plus_one,fold)
            return output

        #def startnewthread(dataset,replicate,partitions):
        #    thread = dataset.replicateThread(replicate,partitions)
        #    thread.start()

class Completeness():
        """The main completeness-assay class."""
	
	def __init__(self,sample_set,parameters,v,r,completeness,contamination,test_configurations,unmodified,numthreads,stratify=False,root_output=None,target_class=None,output_filename=None):
		self.sample_set = sample_set
		self.parameters = parameters
		self.v = v
		self.r = r
                self.w = len(completeness)
                self.z = len(contamination)
                self.unmodified = unmodified
                self.completeness=completeness
                self.contamination=contamination
                self.numthreads=numthreads
		self.test_configurations = test_configurations
		self.root_output = root_output
		self.target_class = target_class
		self.outputFilename = output_filename
	
	def _randomize_sample_set(self):
		self.sample_set.randomize()
	
	
        def _split_sample_set(self,v):
                #split in a way, that 1/v of samples from each category are in test set and (v-1)/v of samples in training set
                index_collection={}
                i=0
                for sample in self.sample_set:
                    categ=sample.get_class_label() #look up how to
                    if not index_collection.get(categ):
                        index_collection[categ]=[]
                    index_collection[categ].append(i)
                    i=i+1

                local_partitions=[]
                for i in xrange(0,v):
                    local_partitions.append([])
                    local_partitions[i]=[]

                i=0
                for categ in index_collection.keys():
                    while len(index_collection[categ]):
                        nextindex=index_collection[categ].pop()
                        local_partitions[i].append([nextindex,nextindex+1]) #double to signal start and end of range
                        i=i+1
                        if i == v:
                            i=0

                return local_partitions


        def _construct_training_and_testing_sets(self, partitions, set_number):
                test_set=self.unmodified.subset(partitions[set_number])
                training_list_list = []
                for i in xrange(len(partitions)):
                    if i != set_number:
                         training_list_list.extend(partitions[i])             	
                training_set = self.sample_set.subset(training_list_list)

                return training_set, test_set
		
	def crossvalidate(self):
		root_output = self.root_output

	
		if self.outputFilename != None:
			rvf_curDate = time.strftime("%Y-%m-%d-%H-%M-%S")
			outputPath = self.outputFilename+"-Files"
			if not os.path.exists(outputPath):
				os.makedirs(outputPath)
                self.replicates=[[[]]*self.z]*self.w
                p=[[[]]*self.v]*self.r
                if self.numthreads<1:
                    self.numthreads=1
                pool=multiprocessing.Pool(self.numthreads)
                tmplist=[]
		for replicate in xrange(self.r):
		    self._randomize_sample_set()
                    self.unmodified=self.unmodified._sort_by_sample_set(self.sample_set) 
		    partitions = self._split_sample_set(self.v)
                    for i in xrange(self.v):
                        training_set, test_set = self._construct_training_and_testing_sets(partitions,i)
                        tmplist.append((training_set,test_set,self,replicate,i))
                self.results=pool.map(replicateProcess, tmplist)
                pool.close()
                pool.join()

#
# used for tabular output classifications/missclassifications. leaving out for contamination/completeness				
		
#	def get_classification_vector(self):
#		"""Return a summary of organisms and what they were classified as."""
#		return self._build_single_vector()
		
		
#	def _build_single_vector(self):
#		"""Cycle through replicates and folds to get a vector of misclassifications"""
#		classifications = {}
#		misclassifications = {}
#		for sample in self.sample_set:
#			who = sample.id
#			for replicate in self.replicates:
#				for results in replicate:
#					if not classifications.has_key(who):
#						classifications[who] = []
#						misclassifications[who] = [0,0]
#					for v in range(len(results)):
#						classification_result = results[v].classifications.get(who,None)
#						if classification_result:
#							#print "Classification results len %d"%(len(classification_result))
#							classifications[who].extend(classification_result)
#							for result in classification_result:
#								if result.predicted_class==result.true_class:
#									misclassifications[who][1] += 1
#								else:
#									misclassifications[who][0] += 1
#		return classifications, misclassifications
					
	def _calculate_mean_and_standard_deviation(self,list):
		mean = 0
		squared_residuals = 0
		for item in list:
			mean += item
		mean = float(mean)/len(list)
		for item in list:
			squared_residuals += (item-mean)**2
		standard_deviation = sqrt(float(squared_residuals)/(len(list)-1))
		return mean, standard_deviation
	
	def get_summary_statistics(self,test_configuration_index):
		"""Return summary statistics over all replicates as a dictionary."""

                summary_statistics=[]
		
                for w in xrange(self.w):
                    summary_statistics.append([])
                    for z in xrange(self.z):
                        summary_statistics[w].append([])
                        f1_scores = []
                        balanced_accuracies = []
                        raw_accuracies = []
                        fn_rate=[]
                        fp_rate=[]
                        mean_f1_score = 0
                        mean_balanced_accuracy = 0
                        mean_raw_accuracy = 0
            		for replicate in self.results:
                            #for fold in replicate[w][z]:
                                        fold=replicate[w][z]
					f1_score = fold.get_F1_score()
					balanced_accuracy = fold.get_balanced_accuracy()
					raw_accuracy = fold.get_raw_accuracy()
                                        tmptuple=fold.get_FN_FP_rate()
                                        fn_rate.append(tmptuple[0])
                                        fp_rate.append(tmptuple[1])
					f1_scores.append(f1_score)
					balanced_accuracies.append(balanced_accuracy)
					raw_accuracies.append(raw_accuracy)

            		mean_f1_score, stddev_f1_score                   = self._calculate_mean_and_standard_deviation(f1_scores)
	        	mean_balanced_accuracy, stddev_balanced_accuracy = self._calculate_mean_and_standard_deviation(balanced_accuracies)
		        mean_raw_accuracy, stddev_raw_accuracy           = self._calculate_mean_and_standard_deviation(raw_accuracies)
                        mean_fn_rate, stddev_fn_rate                     = self._calculate_mean_and_standard_deviation(fn_rate)	
                        mean_fp_rate, stddev_fp_rate                     = self._calculate_mean_and_standard_deviation(fp_rate)	
		
        		summary_statistics[w][z] = {"completeness": self.completeness[w],
                                                        "contamination": self.contamination[z],
                                                        "mean_f1_score":mean_f1_score,
							"mean_balanced_accuracy":mean_balanced_accuracy,
							"mean_raw_accuracy":mean_raw_accuracy,
							"stddev_f1_score":stddev_f1_score,
							"stddev_balanced_accuracy":stddev_balanced_accuracy,
							"stddev_raw_accuracy":stddev_raw_accuracy,
                                                        "mean_fn_rate":mean_fn_rate,
                                                        "stddev_fn_rate":stddev_fn_rate,
                                                        "mean_fp_rate":mean_fp_rate,
                                                        "stddev_fp_rate":stddev_fp_rate}
		return summary_statistics
		
