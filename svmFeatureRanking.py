"""
Extract the most important features of an SVM model, i.e. the COGs/NOGs with
the highest predicted impact on presence/absence of the phenotype.
This is done by calculating the primal variable w (weights vector), which is:
    w = SUM_i ( SVcoeff_i * SV_i )
and considering those dimensions with the highest absolute value.

NOTE: This only applies to linear SVM models, which are standard in PICA.
DO NOT use for other kernels like RBF etc. 
See: http://jmlr.org/proceedings/papers/v3/chang08a/chang08a.pdf

@author: Roman V. Feldbauer
@date: 2015-02-03
"""

class SVMmodelError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def readMetadata(model):  
    metadata = {}  
    processedMetadata = 0    
    for line in model:
        if line.startswith('svm_type') and not metadata.has_key('svm_type'):
            metadata['svm_type'] = line.split()[-1]
            processedMetadata += 1
        elif line.startswith('kernel_type') and not metadata.has_key('kernel_type'):
            metadata['kernel_type'] = line.split()[-1]
            processedMetadata += 1
        elif line.startswith('nr_class') and not metadata.has_key('nr_class'):
            metadata['nr_class'] = int( line.split()[-1] )
            processedMetadata += 1
        elif line.startswith('total_sv') and not metadata.has_key('total_sv'):
            metadata['total_sv'] = int( line.split()[-1] )
            processedMetadata += 1
        elif line.startswith('rho') and not metadata.has_key('rho'):
            metadata['rho'] = float( line.split()[-1] )
            processedMetadata += 1
        elif line.startswith('label') and not metadata.has_key('label'):
            labels = line.split()
            if len(labels) > 3:
                raise SVMmodelError('Not binary classification')
            elif len(labels)-1 != metadata['nr_class']:
                raise SVMmodelError('nr_class and actual number of classes do not match')
            else:
                del labels[0]
                metadata['label'] = [int(label) for label in labels]
            processedMetadata += 1
        elif line.startswith('nr_sv') and not metadata.has_key('nr_sv'):
            numberOfSVs = line.split()
            if len(numberOfSVs)-1 != metadata['nr_class']:
                raise SVMmodelError('nr_class does not match the number of entries in nr_sv')
            else:
                del numberOfSVs[0]
                metadata['nr_sv'] = [int(number) for number in numberOfSVs]
            if sum(metadata['nr_sv']) != metadata['total_sv']:
                raise SVMmodelError('Numbers of support vectors per class do not add up to total_sv')
            processedMetadata += 1
        elif line.startswith('SV'):
            # do nothing, this line only indicates the start of SV block
            processedMetadata += 1
        else:
            if processedMetadata != 8: # expecting metadata in lines 0..7, SVs from line 8
                raise SVMmodelError('Meta data error')
            else:
                #everything alright!
                pass
    #for debugging purposes
    #print metadata
    
    return metadata
    
def readSupportVectors(model, metadata):
    # MAGIC number 8: Lines of metadata in an SVM model
    # TODO remove magic number
    numberOfFeatures = len(model[8].split()) - 1
    numberOfSVs = len(model) - 8
    assert numberOfSVs == metadata['total_sv'], \
        "The number of support vectors according to metadata does not " + \
        "match the number that is present in the actual data set."
    
    # TODO immediately create numpy array instead of general list
    sv = [[0 for svector in range(numberOfSVs)] for feature in range(numberOfFeatures)]
    svCoeff = [0.0 for svector in range(numberOfSVs)] 
    
    for line in xrange(8, len(model)):
        currentSupportVector = model[line].split()
        svCoeff[line-8] = float( currentSupportVector[0] )
        del currentSupportVector[0]
        if len(currentSupportVector) != numberOfFeatures:
            raise SVMmodelError('support vectors have different dimensionality')
        
        for dataPoint in currentSupportVector:
            presenceValue = int( dataPoint.split(':')[-1] )
                        
            if presenceValue == 1:
                feature = int( dataPoint.split(':')[0] )
                sv[feature][line-8] = 1
            # no need to handle presenceValue=0, since matrix was init as zeros
    
    return sv, svCoeff 

def calculateWeightsVector(sv, svCoeff):
    assert len(sv[0]) == len(svCoeff), \
        "SV matrix and svCoeff vector dimensionality do not match.\n" + \
        "SV matrix is %d x %d, svCoeff vector is %d x 1" % \
        (len(sv), len(sv[0]), len(svCoeff))
    #print "DEBUG:", str(len(sv)), str(len(sv[0])), str(len(svCoeff)) 
    
    svMatrix = numpy.array(sv)
    svCoeffVector = numpy.array(svCoeff)
    #print "DEBUG:", str(len(svMatrix)), str(len(svMatrix[0])), str(len(svCoeffVector))
    w = svMatrix.dot(svCoeffVector)
    #print "DEBUG:", w 
    
    return w

def rankDimensions(w):
    """ return a list of sorted indices of w  """
    return sorted(range(len(w)), key=lambda k: abs(w[k]), reverse=True)
    
def readFeatureMap(featureMapFile):
    with open(featureMapFile, 'r') as handle:
        featureMap = pickle.loads(handle.read())
    return featureMap

def readClassLabelMap(classLabelMapFile):
    with open(classLabelMapFile, 'r') as handle:
        classLabelMap = pickle.loads(handle.read())
    return classLabelMap

def readNogDescription(nogDescriptionFile):
    nogDescriptionDict = {}
    with open(nogDescriptionFile, 'r') as handle:
        lines = handle.readlines()
    for line in lines:
        words = line.split('\t')
        nogDescriptionDict[words[0]] = words[1].strip()    
    return nogDescriptionDict

def determinePredictionClass(w, args):
    if args.clmi:
        clmi = readClassLabelMap(args.clmi)
    elif os.path.isfile(args.model + ".classlabelmapindex"):
        clmi = readClassLabelMap(args.model + ".classlabelmapindex")
    else:
        raise SVMmodelError("Could not find class label map index file")
    
    if clmi[0] == 'YES' and clmi[1] == 'NO':
        pass
    elif clmi[0] == 'NO' and clmi[1] == 'YES':  
        w = [-w_i if w_i != 0 else w_i for w_i in w]    #change the sign unless zero
    else:
        raise SVMmodelError("Class label map index is supposed to have values " + \
            "'YES' and 'NO', but is has %r and %r" % (clmi[0], clmi[1]) )
            
    return w
            
def printFeatureRanking(w, dimRank, args):
    if args.fmi:
        fmi = readFeatureMap(args.fmi)
    elif os.path.isfile(args.model + ".featuremapindex"):
        fmi = readFeatureMap(args.model + ".featuremapindex")
    else:
        raise SVMmodelError("Could not find feature map index file")    
    
    descriptionHeader = ''
    description = ''
    if args.descr:
        nogDescription = readNogDescription(args.descr)      
        descriptionHeader = '\tGroup_description'


    ranking=[]
    featureGroup_list=[]
    featureGroups_count=0
    absLastRank = 2.0
    relevanceThreshold = abs(w[dimRank[0]]) * (1 - args.range/100.0 )
    for rank in dimRank:
        assert abs(w[rank]) <= absLastRank, "Feature ranking list appears not to be sorted. " + \
            "%r <= %r evaluated to False" % (abs(w[rank]), absLastRank)
        if abs(w[rank]) >= relevanceThreshold:
            if w[rank] >= 0:
                predictorForClass = 'YES'
            else:
                predictorForClass = 'NO'
            # if fmi[rank].find('/') != -1:     #Several COGs/NOGs might be grouped together because of same profile 
            featureGroup = fmi[rank].split('/') # ...need to be split on FS '/'

            # PH
            # collect compressed features as groups and write only "FeatureGroupX\tweight" and group to separate file (outputfile).groups


            if len(featureGroup) > 1:
                featureGroup_list.append(featureGroup)
                featureGroups_count=featureGroups_count+1
                ranking.append(("FeatureGroup"+str(featureGroups_count),str(w[rank]),predictorForClass,description))
            else:
                ranking.append((featureGroup[0],str(w[rank]),predictorForClass,description))

            absLastRank = abs(w[rank])
        else:
            break
    output_base=".".join(args.model.split(".")[:-1])
    with open(output_base + ".rank","w") as rank_file:
        rank_file.write("Group_ID\tScore\tClass"+descriptionHeader+"\n")
        for featureRank in ranking:
            rank_file.write("\t".join(featureRank)+"\n")

    with open(output_base + ".rank.groups","w") as group_file:
        group_file.write("Group_ID\tFeatures\n")
        for index in range(0,len(featureGroup_list)):
            group_file.write("FeatureGroup"+str(index+1)+"\t"+"/".join(featureGroup_list[index])+"\n")
            # /PH       

 
def checkArguments(args):
    if not os.path.isfile(args.model):
        print "ARGUMENT ERROR: SVM model file does not exist"
        exit(1)
    if args.clmi and not os.path.isfile(args.clmi):
        print "ARGUMENT ERROR: Class label map index file does not exist"
        exit(1)
    if args.fmi and not os.path.isfile(args.fmi):
        print "ARGUMENT ERROR: Feature map index file does not exist"
        exit(1)
    if args.range < 0 or args.range > 100:
        print "ARGUMENT ERROR: Range must be an integer in [0, 100]"
        exit(1)
    if args.descr and not os.path.isfile(args.descr):
        print "ARGUMENT ERROR: NOG description file could not be found"
        exit(1)

#######################################
#
#            MAIN PROGRAM
#
#######################################
#    
# outline
# 1. Read SVM model 
# 2. Save SVs and SV_coeffs in numpy vectors 
# 3. Calculate w 
# 4. Select top ranking dimensions 
# 5. Read classlabelmapindex and featuremapindex
# 6. Map dimensions to features and determine whether pos/neg phenotype predictor 
# 7. Output sorted list of COGs/NOGs and their scores

import argparse
import numpy
import pickle
import os

defaultRange = 100
rangeHelp="""Restrict output to top features only. The highest ranking feature is returned 
as well as those features with scores that are <= N percent lower 
[N=0 ... only top feature, N=100 ... complete feature list, default: N=%d]""" % defaultRange
parser = argparse.ArgumentParser(version="SVM feature ranking")
parser.add_argument("model", action="store", help="SVM model FILE", metavar="FILE")
parser.add_argument("-r","--range",action="store",dest="range", help=rangeHelp, metavar="N", type=int, default=defaultRange)
parser.add_argument("-c","--class_label",action="store",dest="clmi", help="Class label map index file corresponding to SVM model", metavar="FILE")
parser.add_argument("-f","--feature_map",action="store",dest="fmi", help="Feature map index file corresponding to SVM model", metavar="FILE")
parser.add_argument("-d","--NOG_description",action="store",dest="descr", metavar="FILE", help="Read NOG descriptions from FILE and add them to the ouput")
args = parser.parse_args()
checkArguments(args)

with open(args.model, 'r') as modelFile:
    model = [line[:-1].strip('\n').strip('\r') for line in modelFile.readlines()]
try:
    metadata = readMetadata(model)
    
    sv, svCoeff = readSupportVectors(model, metadata) 
      
    w = calculateWeightsVector(sv, svCoeff) 
    
    dimRank = rankDimensions(w) 
    
    w = determinePredictionClass(w, args)
    
    printFeatureRanking(w, dimRank, args)
    
except SVMmodelError as err:
    print "ERROR: While parsing the SVM model, the following error occurred:", err.value
