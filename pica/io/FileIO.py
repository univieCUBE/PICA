"""
Base class for reading samples.

@author: Norman MacDonald
@date: 2010-02-16
"""

from __future__ import print_function
import sys, os
from sklearn.externals import joblib
from pica.Sample import SampleSet, ClassLabelSet
from pica.DataCollection import DataCollection


def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)

def fileExists(filename):
    if not (os.path.exists(filename) and os.path.getsize(filename) > 0):
        error("File %r does not exist or has size 0." % filename)
        exit(1)
    else:
        return True

class FileIO():
    def __init__(self):
        pass

    # RVF
    # changed this function, so that SVM models are treated correctly,
    # i.e. index-attribute mapping needs to match that used in the model.
    # (Otherwise, COGs in the test set most probably do not get the same
    # SVM dimension id that was used for training.)
    def load_samples(self,filename, indexToAttribute=None):
        """Load samples from a tab delimited file."""
        fileExists(filename)
        fin = open(filename)
        data = fin.readlines()
        fin.close()
        "First, get a list of all attributes"

        if indexToAttribute != None: # RVF this part is new (as explained above) for SVM
            # Instead of generating new index-attribute mapping as above,
            # import the mapping created while training.
            #with open(indexToAttribute+".featuremapindex", 'rb') as handle:
            index_to_attribute = joblib.load(indexToAttribute+".featuremapindex")
            attribute_to_index = {}
            for index, attribute in enumerate(index_to_attribute):
                        # PH fixed problem with compressed features
                                attribute_split=attribute.split("/")
                                for attribute in attribute_split:
                                    attribute_to_index[attribute] = index
            max_attribute = len(index_to_attribute)
            nattributes = max_attribute #+ 1

        else: # for CPAR
            attribute_to_index = {}
            index_to_attribute = []
            nattributes = 0

            # in both cases: read file. For SVM, this only adds new features
            # that were not present in the training set. Otherwise, add all
            # of them.
            # HP: this is obviously not needed for SVM-test - libSVM ignored additional features,
            # but sklearn does not! only needed for training..
            for row in data:
                fields = (x.strip() for x in row.split()[1:])
                for field in fields:
                    if not attribute_to_index.has_key(field):
                        attribute_to_index[field] = nattributes
                        index_to_attribute.append(field)
                        nattributes += 1

        max_attribute = nattributes - 1

        sample_set = SampleSet(max_attribute)

        sample_set.feature_to_index = attribute_to_index
        sample_set.index_to_feature = index_to_attribute


        for line in data:
            fields = [x.strip() for x in line.split()]
            if len(fields) > 0:
                who = fields[0]
                #attributes = map(lambda f: sample_set.feature_to_index[f.strip()],fields[1:])
                #replacing the one-liner to append only if present in feature-to-index
                attributes = []
                for f in fields[1:]:
                    fti = sample_set.feature_to_index.get(f.strip())
                    if fti:
                        attributes.append(fti)
                sample_set.add_sample(who,attributes)
            else:
                pass #skip empty line

        return sample_set

    def load_metadata(self,filename):
        fileExists(filename)
        data_collection = DataCollection()
        data_collection = data_collection.load_data_collection(filename)
        return data_collection


    def save_samples(self,sample_set,filename,sep="\t"):
        fout = open(filename,"w")
        for sample in sample_set:
            outline = [sample.id]
            string_list = sample.get_attributes_string_list()
            string_list.sort()
            outline.extend(string_list)
            fout.write("%s\n"%(sep.join(outline)))
        fout.close()

    def load_classes(self,filename):
        """Load class labels from a tab delimited file."""
        fileExists(filename)
        class_label_set = ClassLabelSet()
        return class_label_set.load_data_collection(filename)

    def init_null_classes(self, filename, targetclass):
        """Load species from file and assign NULL values to the targetclass ."""
        class_label_set = ClassLabelSet()
        cls = class_label_set.null_data_collection(filename, targetclass)

        return cls


