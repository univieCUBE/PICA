"""
sklearnSVM Classification interface.  The input model must be a sklearn model.

@author: Patrick Hyden
@date: 2017-11-20
"""

import time
import operator
from pica.classifiers.BaseClassifier import BaseClassifier
from pica.ClassificationResults import ClassificationResults

class sklearnSVMClassifier(BaseClassifier):
    """sklearnSVM Classification implementation."""

    def __init__(self,svc_object):
        self.parameters = svc_object.get_params()
        self.null_flag = "NULL"
        self.model = svc_object

    def load_model(self,model_filename):
        return None
        #load_rules(model)

    def test(self,lstSamples,model):
        """Test the SVM classifier on the sample set and return the ClassificationResults."""

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
        sample_vector = [int(x) for x in sample.get_attribute_matrix()]
        samples=[[sample_vector]]
        #adding support for probability models!
        if self.parameters.probability == True:
            probs = self.model.predict_proba(samples)
            best_class_index, prob = max(enumerate(probs), key=operator.itemgetter(1))
        else:
            best_class_index = int(self.model.predict.predict(samples))
            prob = "NA"
        return model["class_label_map_index"][int(best_class_index)], prob