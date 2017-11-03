"""
Interface to training with libSVM.

LIBSVM is a third party application with Python API from http://www.csie.ntu.edu.tw/~cjlin/libsvm/

@author Norman MacDonald (norman@cs.dal.ca)
"""
from libsvm290.python.svm import *
from pica.trainers.BaseTrainer import BaseTrainer
import sys
import os


class libSVMTrainer(BaseTrainer):
	KERNEL_TYPES = {"LINEAR":LINEAR,"RBF":RBF,"POLY":POLY,"SIGMOID":SIGMOID}
	SVM_TYPES = {"C_SVC":C_SVC,"NU_SVC":NU_SVC,"ONE_CLASS":ONE_CLASS,"EPSILON_SVR":EPSILON_SVR,"NU_SVR":NU_SVR}
	
	def __init__(self,parameters_filename=None,kernel_type=None,C=None,probability=1):
		"Load defaults"
		
		libSVMTrainer.default_parameters = svm_parameter.default_parameters.copy()
		self.param = libSVMTrainer.default_parameters.copy()
		p = {}
		
		"PICA defaults"
		p["C"] = 5
		p["kernel_type"] = "LINEAR"
		#p["kernel_type"] = "RBF"
		#p["kernel_type"] = "POLY"
		#p["kernel_type"] = "SIGMOID"
                p["probability"] = 1
		
		
		"Overrides from file"
		if parameters_filename:
			if os.path.isfile(parameters_filename):	
				p = self.load_parameters(parameters_filename) 
			else:
				print "Parameter file could not be found, using defaults instead"

		"Overrides from method call parameters"
		if kernel_type:
			p["kernel_type"] = kernel_type
		if C:
			p["C"] = C
		
		print "Parameters modified from LIBSVM default: %s"%(p)
		self.param.update(p)
		self.null_flag = "NULL"
	
	
	def train(self,samples):
		
		attribute_lens = {}
		current_class_label_index = 0
		class_label_map = {}
		class_labels = []
		sample_attributes = []
		class_label_map_integer = []
		for sample in samples:
			sample_class_label = sample.get_class_label()
			current_vector = [int(x) for x in sample.get_attribute_matrix()]
			sample_attributes.append(current_vector)
			attribute_lens[len(current_vector)] = 1
			if not class_label_map.has_key(sample_class_label):
				class_label_map[sample_class_label] = current_class_label_index
				current_class_label_index += 1
				class_label_map_integer.append(sample_class_label)
			class_labels.append(class_label_map[sample_class_label])
		prob = svm_problem(class_labels,sample_attributes)
		default = libSVMTrainer.default_parameters
		print self.param["kernel_type"]
		kernel_type = libSVMTrainer.KERNEL_TYPES.get(self.param["kernel_type"],default["kernel_type"])
		svm_type = libSVMTrainer.SVM_TYPES.get(self.param["svm_type"],default["svm_type"])
		C = float(self.param["C"])
		gamma = int(self.param["gamma"])
		degree = int(self.param["degree"])
		coef0 = int(self.param["coef0"])
		nu = float(self.param["nu"])
                b = int(self.param["probability"])
		print "Starting svm (svm_type=%s,kernel_type=%s,C=%f,gamma=%f,probability=%i)"%(svm_type,kernel_type,C,gamma,b)
		svm_param = svm_parameter(kernel_type = kernel_type, 
					svm_type = svm_type,
					C = C, 
					gamma = gamma,
					degree = degree,
					coef0 = coef0,
					nu = nu, probability = b)
	
					
		
		m = svm_model(prob, svm_param)
		return {"svm_model":m,"class_label_map":class_label_map,"class_label_map_index":class_label_map_integer}
