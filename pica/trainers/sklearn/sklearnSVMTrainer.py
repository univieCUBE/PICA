"""
Interface to training with scikit-learn.

@author Patrick Hyden
"""
import numpy as np
from sklearn import svm
from pica.trainers.BaseTrainer import BaseTrainer
import os


class sklearnSVMTrainer(BaseTrainer):
    kernel_types=["linear","rbf","sigmoid","poly"]

    def __init__(self,parameter_file=None,C=None,probability=None,kernel_type=None):
        "PICA defaults"
        self.param = {"C":5,"gamma":"auto","kernel_type":"linear", "probability":0}
        #p["C"] = 5
        #p["gamma"] = 'auto'
        #p["kernel_type"] = "LINEAR"
        #p["kernel_type"] = "RBF"
        #p["kernel_type"] = "POLY"
        #p["kernel_type"] = "SIGMOID"
        #p["probability"] = 0


        "Overrides from method call parameters"
        kernel_type=kernel_type.lower()
        if kernel_type in sklearnSVMTrainer.kernel_types:
            self.param["kernel_type"] = kernel_type
        if C:
            self.param["C"] = C
        if probability:
            self.param["probability"] = True
        else:
            self.param["probability"] = False

        print "Parameters modified from default: %s"%(self.param)
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
        svm_type="sklearn_svm_classifier"
        kernel_type = self.param["kernel_type"]
        C = float(self.param["C"])
        gamma = self.param["gamma"]
        b = self.param["probability"]
        print "Starting svm (svm_type=%s,kernel_type=%s,C=%f,gamma=%s,probability=%d)"%(svm_type,kernel_type,C,str(gamma),b)
        svm_classifier = svm.SVC(kernel = kernel_type, C = C, gamma = gamma, probability = b)

        svm_classifier.fit(np.array(sample_attributes), np.array(class_labels))
        return {"svm_model":svm_classifier,"class_label_map":class_label_map,"class_label_map_index":class_label_map_integer}
