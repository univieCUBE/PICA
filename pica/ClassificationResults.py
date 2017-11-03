"""
Store the results and statistics of a classification algorithm.

@author: Norman MacDonald
@date: 2010-02-16
"""
class ClassificationResult:
	def __init__(self,who,predicted_class,true_class,prob):
		self.who = who
		self.predicted_class = predicted_class
		self.true_class = true_class
                self.prob = prob
		
	def __str__(self):
		return "%s\t%s\t%s\t%s"%(self.who,self.true_class,self.predicted_class,str(prob))
	
	def getSpeciesPrediction(self):
		return [self.who, self.predicted_class, str(self.prob)]

class ClassificationResults:
	"""Store the results and statistics of a classification algorithm."""
	
	def __init__(self,positive_class="YES"):
		"""Initialize a confusion matrix."""
		self._positive_class = positive_class
		self.unclassified = 0
		self.classifications = {}
		self.classifications_list = []
		
	def set_positive_class(self,positive_class):
		"""Change the positive class label."""
		self._positive_class = positive_class
		
	def add_classification(self,who,predicted_class,true_class,prob):
		if predicted_class == None:
			predicted_class = "NULL"
		if true_class == None:
			true_class = "NULL"
		classification_result = ClassificationResult(who,predicted_class,true_class,prob)
		if not self.classifications.has_key(who):
			self.classifications[who] = []
		self.classifications[who].append(classification_result)
		self.classifications_list.append(classification_result)
		
		
	def get_classification(self,who=None,index=None):
		"""Return a the classification result for who"""
		classification_result = None
		if who!=None:
			classification_result =  self.classifications.get(who,None)
		elif index!=None:
			classification_result = self.classifications_list[index]
		else:
			raise Exception("You must provide a key or index.")
		return classification_result
	
	def sum_confusion_matrix(self):
		"""Return the sum over all entries of the confusion matrix."""
		return len(self.classifications_list)
		
	def get_raw_accuracy(self):
		"""Return the ratio of correctly classified to total classified."""
		total_correct = 0
		accuracy = 0.0
		for classification in self.classifications_list:
			if classification.predicted_class == classification.true_class:
				total_correct += 1
		total = self.sum_confusion_matrix()
		if total_correct > 0:
			accuracy = float(total_correct)/total
		return accuracy
	
	def _get_class_labels(self):
		labels = {}
		for classification in self.classifications_list:
			labels[classification.predicted_class] = 1
			labels[classification.true_class] = 1
		return sorted(labels.keys())
	
	def get_balanced_accuracy(self):
		"""Return the raw accuracy averaged over each class label."""
		class_labels = self._get_class_labels()
		nclasses = 0
		accuracy = 0

		for actual in class_labels:
			if actual != "NULL" and actual != None:
				nclasses+=1
				correct = 0
				incorrect = 0
				for classification in self.classifications_list:
					if classification.true_class == actual:
						if classification.predicted_class == actual:
							correct += 1
						else:
							incorrect += 1
				if correct > 0:
					accuracy += float(correct)/(correct+incorrect)
		return float(accuracy)/nclasses


        #def get_false_positive_rate(self):
        #        """Return the raw accuracy averaged over each class label."""
        #        class_labels = self._get_class_labels()
        #        nclasses = 0
        #        tn = 0

		
	def get_F1_score(self):
		"""Return the F1 score for comparison with netCAR"""
		precision = 0
		sensitivity = 0
		f1_score = 0
		
		#Confusion matrix: cm[actual][predicted]
		cm = self.build_confusion_matrix()
		tp=0
		tn=0
		fp=0
		fn=0
		nullpos=0
		nullneg=0
		if (cm.has_key('YES')):
			if (cm['YES'].has_key('YES')):
				tp = cm['YES']['YES']
			if (cm['YES'].has_key('NO')):
				fn = cm['YES']['NO']
			if ( cm['YES'].has_key('NULL') ): 
				nullpos = cm['YES']['NULL']
		if (cm.has_key('NO')):
			if (cm['NO'].has_key('YES')):
				fp = cm['NO']['YES']
			if (cm['NO'].has_key('NO')):
				tn = cm['NO']['NO']
			if ( cm['NO'].has_key('NULL') ): 
				nullneg = cm['NO']['NULL']		
		
		if (tp+fp > 0):
			precision = float(tp) / (tp+fp)	# test outcome pos
		if ((tp+fn)>0):
			sensitivity = float(tp) / (tp+fn) #condition pos
		if (precision*sensitivity > 0):
			f1_score = 2 * (precision*sensitivity) / (precision+sensitivity)
		return f1_score

        def get_FN_FP_rate(self):
                """Return the FN, FP rates"""
                fn_rate = 0
                fp_rate = 0
                
                #Confusion matrix: cm[actual][predicted]
                cm = self.build_confusion_matrix()
                tp=0
                tn=0
                fp=0
                fn=0
                nullpos=0
                nullneg=0
                if (cm.has_key('YES')):
                        if (cm['YES'].has_key('YES')):
                                tp = cm['YES']['YES']
                        if (cm['YES'].has_key('NO')):
                                fn = cm['YES']['NO']
                        if ( cm['YES'].has_key('NULL') ):
                                nullpos = cm['YES']['NULL']
                if (cm.has_key('NO')):
                        if (cm['NO'].has_key('YES')):
                                fp = cm['NO']['YES']
                        if (cm['NO'].has_key('NO')):
                                tn = cm['NO']['NO']
                        if ( cm['NO'].has_key('NULL') ):
                                nullneg = cm['NO']['NULL']

                if (fn+tp > 0):
                        fn_rate = float(fn) / (fn + tp)
                        fp_rate = float(fp) / (fp + tn)
                return fn_rate, fp_rate
	
	def build_confusion_matrix(self):
		"""Build a dictionary [actual][predicted] of classification results."""
		cm = {}
		class_labels = self._get_class_labels()
		for class_labela in class_labels:
			cm[class_labela] = {}
			for class_labelb in class_labels:
				cm[class_labela][class_labelb] = 0
		for classification in self.classifications_list:
			cm[classification.true_class][classification.predicted_class] += 1
		return cm
	
	def __str__(self):
		"""Return a string summarizing the statistics and confusion matrix."""
		sout = []
		sout.append("Raw accuracy:\t%f"%(self.get_raw_accuracy()))
		sout.append("Bal accuracy:\t%f"%(self.get_balanced_accuracy()))
		# RVF
		sout.append("F1 score:\t%f"%(self.get_F1_score()))
		#/RVF
		confusion_matrix = self.build_confusion_matrix()
		keys = self._get_class_labels()
		keys.sort(reverse=True)
		sout.append("->Pred\t%s"%("\t".join(keys)))
		
		for actualkey in keys:
			matrix_row = []
			matrix_row.append("%s"%(actualkey))
			for predictedkey in keys:
				matrix_row.append("%d"%(confusion_matrix[actualkey][predictedkey]))
			sout.append("\t".join(matrix_row))
		
		return "\n".join(sout)
		
	def print_classification_log(self):
		print "Organism\tTrue\tPredicted\tProbability"
		for c in self.classifications_list:
			print c
			
	def print_classification_log_predictedOnly(self):
		print "Organism\tPredicted\tProbability"
		for c in self.classifications_list:
			print "\t".join(c.getSpeciesPrediction())


class ClassificationSummary:
        """New return object to avoid transfer of large data between separate processes"""

        def __init__(self, results):
            self.raw_accuracy = results.get_raw_accuracy()
            self.FN_rate, self.FP_rate = results.get_FN_FP_rate()
            self.F1_score = results.get_F1_score()
            self.balanced_accuracy = results.get_balanced_accuracy()

        def get_raw_accuracy(self):
            return self.raw_accuracy

        def get_FN_FP_rate(self):
            return self.FN_rate, self.FP_rate

        def get_F1_score(self):
            return self.F1_score

        def get_balanced_accuracy(self):
            return self.balanced_accuracy
