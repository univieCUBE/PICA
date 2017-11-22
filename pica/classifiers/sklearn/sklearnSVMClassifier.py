"""
sklearnSVM Classification interface.  The input model must be a sklearn model.

@author: Patrick Hyden
@date: 2017-11-20
"""

import time
import operator
from pica.classifiers.BaseClassifier import BaseClassifier
from pica.ClassificationResults import ClassificationResults
import numpy as np

class sklearnSVMClassifier(BaseClassifier):
    """sklearnSVM Classification implementation."""

    def __init__(self):
        self.parameters = {}
        self.null_flag = "NULL"

    def load_model(self,model_filename):
        return None
        #load_rules(model)

    def test(self,lstSamples,model):
        """Test the SVM classifier on the sample set and return the ClassificationResults."""
        self.parameters=model["svm_model"].get_params()
        classification_results = ClassificationResults()
        #print "Testing on %d samples"%(len(lstSamples))
        for sample in lstSamples:
            #if sample.get_class_label() != self.null_flag:	# RVF
            if True: # RVF. Also classify the sample, if the class is previously unknown
                best_class, prob = self.classify(sample,model)
                classification_results.add_classification(sample.id,best_class,sample.get_class_label(), prob)
        return classification_results


    def classify(self,sample,model):
        """Classify a single sample with the model."""
        sample_vector = np.array([[int(x) for x in sample.get_attribute_matrix()]])
        #adding support for probability models!
        if self.parameters["probability"] == True:
            probs = model["svm_model"].predict_proba(sample_vector)
            best_class_index, prob = max(enumerate(probs[0]), key=operator.itemgetter(1))
        else:
            best_class_index = int(model["svm_model"].predict(sample_vector))
            prob = "NA"
        return model["class_label_map_index"][int(best_class_index)], prob