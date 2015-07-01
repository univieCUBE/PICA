"""Get the mutual information shared between samples in file 1 with class labels in file 2 with taxonomy levels in file 3 and output to file 4"""

import sys


samples_filename = sys.argv[1]
class_labels_filename = sys.argv[2]
metadata_filename = sys.argv[3]
output_filename = sys.argv[4]

from pica.Sample import SampleSet, ClassLabelSet
from pica.io.FileIO import FileIO
from pica.IntegerMapping import IntegerMapping
from pica.trainers.cwmi.CWMILibrary import CWMILibrary

fileio = FileIO()
cwmilibrary = CWMILibrary()
metadata = fileio.load_metadata(metadata_filename)
samples = fileio.load_samples(samples_filename)
classes = fileio.load_classes(class_labels_filename)
samples.load_class_labels(classes)
confounders = metadata.get_key_list()[1:]

outlines = []
header_line = ["phenotype"]

header_line.extend(confounders)
header_line.append("total")
outlines.append("\t".join(header_line))

for class_name in classes.get_classes():
	"generate phenotype map"
	
	samples.set_current_class(class_name)
	samples.hide_nulls(class_name)
	outline = [class_name]
	list_Y = []
	for sample in samples:
		if not sample.is_null_class():
			label = sample.get_class_label(class_name)
			list_Y.append(label)
	im_classes = IntegerMapping()
	v_Y = im_classes.calculate_new_integer_map_for_list(list_Y)
	v_Y_entropy = cwmilibrary.calculate_entropy(v_Y)
	for confounder in confounders:
		"generate confounder map"
		list_Z = []
		for sample in samples:
			if not sample.is_null_class():
				c = metadata[sample.id][confounder]
				list_Z.append(c)
		im_confounders = IntegerMapping()
		v_Z = im_confounders.calculate_new_integer_map_for_list(list_Z)
		mi = cwmilibrary.calculate_mi(v_Y,v_Z)
		remaining_i = v_Y_entropy - mi
		outline.append(str(remaining_i))
		#outline.append(str(mi))
	outline.append(str(v_Y_entropy))
	outlines.append("\t".join(outline))
	samples.unhide_all()
fout = open(output_filename,"w")
fout.write("\n".join(outlines))
fout.close()



#TEMP WRITE OUT DISTRIBUTIONS
outlines = []
header_line = ["taxon level","group","phenotype","value","count"]

outlines.append("\t".join(header_line))
output = {}
for class_name in classes.get_classes():
	"generate phenotype map"
	samples.set_current_class(class_name)
	samples.hide_nulls(class_name)
	for confounder in confounders:
		"generate confounder map"
		list_Z = []
		for sample in samples:
			c = metadata[sample.id][confounder]
			p = sample.get_class_label(class_name)
			key = (confounder,c,class_name,p)
			if not output.has_key(key):
				output[key] = 0
			output[key]+=1
		
	samples.unhide_all()

	
fout = open("distributions.txt","w")
outlines = []
for key in output.keys():
	outline = list(key)
	outline.append(str(output[key]))
	outlines.append("\t".join(outline))
fout.write("\n".join(outlines))
fout.close()
		

