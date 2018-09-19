"""
Take a set of samples and labels, randomly sort and V-fold cross-validate R times with X completeness

@author: Norman MacDonald
@date: 2010-02-19

"""
from ClassificationResults import ClassificationResults
from math import sqrt

from pica.io.FileIO import FileIO
from pica.Sample import SampleSet
import time
import os
import pickle

import sys
MPI_PARALLEL = False
class Completeness():
	"""The main completeness-assay class."""
	
	def __init__(self,sample_set,parameters,v,r,completeness,contamination,test_configurations,unmodified,stratify=False,root_output=None,target_class=None,output_filename=None):
		self.replicates = []
		self.sample_set = sample_set
		self.parameters = parameters
		self.v = v
		self.r = r
                self.unmodified = unmodified
                #print(dir(unmodified))
                #print(dir(sample_set))
                self.completeness=completeness
                self.contamination=contamination
		self.test_configurations = test_configurations
		self.root_output = root_output
		self.target_class = target_class
		self.outputFilename = output_filename
		#self.training_object = training_object
		#self.testing_object = testing_object
	
	def _randomize_sample_set(self):
		self.sample_set.randomize()
		
	
	def _split_sample_set(self,v):
		"""Return indices for v-way split of sample set"""
		indices = []
		len_sample_set = len(self.sample_set)
		set_size = float(len_sample_set)/v
		cindex = 0
		while cindex < len(self.sample_set):
			indices.append(int(cindex))
			cindex += set_size #set_size may be fractional
		return indices
		
	def _construct_training_and_testing_sets(self, partitions, set_number):
		local_partitions = partitions[:]
		local_partitions.append(len(self.sample_set))
		test_set = self.unmodified.subset(((local_partitions[set_number],local_partitions[set_number+1]),))
		training_list_list = []
		for i in xrange(len(partitions)):
			if i != set_number:
				training_list_list.append((local_partitions[i],local_partitions[i+1]))
		training_set = self.sample_set.subset(training_list_list)
		
                return training_set, test_set
		
		
	def crossvalidate(self):
		root_output = self.root_output
		
		if self.outputFilename != None:
			rvf_curDate = time.strftime("%Y-%m-%d-%H-%M-%S")
			outputPath = self.outputFilename+"-Files"
			if not os.path.exists(outputPath):
				os.makedirs(outputPath)
		

		for replicate in xrange(self.r):
			if MPI_PARALLEL:
				pass
			else:
				replicate_plus_one = replicate+1
				print "Starting replicate %d"%(replicate_plus_one)
				self.replicates.append([])
				self._randomize_sample_set()
                                self.unmodified=self.unmodified._sort_by_sample_set(self.sample_set) 
				partitions = self._split_sample_set(self.v)
				for i in xrange(self.v):
					self.replicates[replicate].append([])
					training_set, test_set = self._construct_training_and_testing_sets(partitions,i)
					print "Fold %d: training_set: %d, test set: %d"%(i,len(training_set),len(test_set))
					
					if ( self.target_class != None ):
						fileio = FileIO()
						trainingSetFile = outputPath+"/"+str(self.target_class)+"_R"+str(replicate)+"_F"+str(i)+"_training.set"
						testSetFile =     outputPath+"/"+str(self.target_class)+"_R"+str(replicate)+"_F"+str(i)+"_test.set"
						print "Saving training set to: "+trainingSetFile
						fileio.save_samples(training_set,trainingSetFile)
						print "Saving test set to: "+testSetFile
						fileio.save_samples(test_set,testSetFile)
		
					for test_configuration in self.test_configurations:
						test_name = test_configuration.name
						new_training_set = training_set
						new_test_set = test_set
						if test_configuration.feature_selector:
							features = test_configuration.feature_selector.select(training_set)
							new_training_set = training_set.feature_select(features)
							new_test_set = test_set.feature_select(features)
						model = test_configuration.trainer.train(new_training_set)
						
						if self.outputFilename != None:
							if not hasattr(model, 'write'): # i.e. probably SVM model
								svmModelFile = outputPath+"/"+str(self.target_class)+"_R"+str(replicate)+"_F"+str(i)+"_svm.model"							
								model['svm_model'].save(filename=svmModelFile)
								with open(svmModelFile+".classlabelmap",'a') as outfile:
									pickle.dump(model["class_label_map"],outfile) #fails with model, because of SWIGpy object
								with open(svmModelFile+".classlabelmapindex",'a') as outfile:
									pickle.dump(model["class_label_map_index"],outfile)
								with open(svmModelFile+".featuremapindex",'w') as outfile:
									pickle.dump(new_training_set.get_index_to_feature(), outfile)




						#####################################################################################
                                                # add here contamination&completeness
                                                #####################################################################################
                                                all_class_labels=new_test_set.get_class_labels()
                                                sample_attribute_collection={}
                                                for index in all_class_labels:
                                                    sample_attribute_collection[index]=[]

                                                for sample in new_test_set.__iter__():
                                                    temp_attributes_list=list(sample.get_attributes_index_list())
                                                    sample_attribute_collection[sample.current_class_label].append(temp_attributes_list)



                                                for w in range(0,len(self.completeness)):
                                                    self.replicates[replicate][i].append([])
                                                    incomplete_test_set = new_test_set.induce_incompleteness(self.completeness[w])


                                                    if len(sample_attribute_collection.keys()) != 2:
                                                        print(sample_attribute_collection.keys())
                                                        sys.stderr.write("Warning: skipping contamination of Fold %i in replicate %i: need exactly 2 different class labels\n" % (i, replicate))
                                                        for z in range(0,len(self.contamination)):
                                                            self.replicates[replicate][i][w].append([])
                                                        continue
                                                    for z in range(0,len(self.contamination)):
                                                        self.replicates[replicate][i][w].append([])
                                                        #print(completeness,contamination)
                                                        contaminated_test_set = incomplete_test_set.introduce_contamination(sample_attribute_collection,self.contamination[z])
                                                        
                                                        contaminated_test_set = contaminated_test_set.map_test_set_attributes_to_training_set(new_training_set) 
                                                        #print(dir(model))

		        				results = test_configuration.classifier.test(contaminated_test_set,model)
			        			self.replicates[replicate][i][w][z].append(results) #order of results same as order of configurations
				        		
					        	if ( self.target_class != None ):
						        	print results.print_classification_log()
							        print results
						
        						if root_output:
	        						fout = open("%(root_output)s.r%(replicate_plus_one)d.v%(i)d.%(test_name)s.features"%(locals()),"w")
		        					fout.write("\n".join(features))
			        				fout.close()
				if root_output:
					
					fout = open("%(root_output)s.r%(replicate_plus_one)d.classification.log"%(locals()),"w")
					header_fields = ["sample","fold",self.sample_set.current_class]
					for test_configuration in self.test_configurations:
						header_fields.append(test_configuration.name)
					output_dictionary = {}
					output_lines = ["\t".join(header_fields)]	
					for fold in xrange(self.v):
						for classification_index in xrange(len(self.replicates[replicate][fold][0].classifications_list)):
							main_sample_record = self.replicates[replicate][fold][0].classifications_list[classification_index]
							output_line = [str(main_sample_record.who),str(fold+1),str(main_sample_record.true_class)]
							for test_configuration_index in xrange(len(self.test_configurations)):
								test_sample_record = self.replicates[replicate][fold][test_configuration_index].classifications_list[classification_index]
								output_line.append(str(test_sample_record.predicted_class))
							output_lines.append("\t".join(output_line))
					fout.write("\n".join(output_lines))
					fout.close()
				print "Finished replicate %d"%(replicate_plus_one)


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
		#f1_scores = []
		#balanced_accuracies = []
		#raw_accuracies = []
		#mean_f1_score = 0
		#mean_balanced_accuracy = 0
		#mean_raw_accuracy = 0

                summary_statistics=[]
		
                for w in range(0,len(self.completeness)):
                    summary_statistics.append([])
                    for z in range(0,len(self.contamination)):
                        summary_statistics[w].append([])
                        f1_scores = []
                        balanced_accuracies = []
                        raw_accuracies = []
                        mean_f1_score = 0
                        mean_balanced_accuracy = 0
                        mean_raw_accuracy = 0
            		for replicate in self.replicates:
	        		for fold in replicate:
                                        fold=fold[w][z]
                                        if len(fold)==0:
                                            continue
					f1_score = fold[test_configuration_index].get_F1_score()
					balanced_accuracy = fold[test_configuration_index].get_balanced_accuracy()
					raw_accuracy = fold[test_configuration_index].get_raw_accuracy()
					f1_scores.append(f1_score)
					balanced_accuracies.append(balanced_accuracy)
					raw_accuracies.append(raw_accuracy)
	
            		mean_f1_score, stddev_f1_score                   = self._calculate_mean_and_standard_deviation(f1_scores)
	        	mean_balanced_accuracy, stddev_balanced_accuracy = self._calculate_mean_and_standard_deviation(balanced_accuracies)
		        mean_raw_accuracy, stddev_raw_accuracy           = self._calculate_mean_and_standard_deviation(raw_accuracies)
		
        		summary_statistics[w][z] = {"completeness": self.completeness[w],
                                                        "contamination level": self.contamination[z],
                                                        "mean_f1_score":mean_f1_score,
							"mean_balanced_accuracy":mean_balanced_accuracy,
							"mean_raw_accuracy":mean_raw_accuracy,
							"stddev_f1_score":stddev_f1_score,
							"stddev_balanced_accuracy":stddev_balanced_accuracy,
							"stddev_raw_accuracy":stddev_raw_accuracy}
		return summary_statistics
		
