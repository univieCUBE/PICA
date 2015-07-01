
Phenotype Investigation with Classification Algorithms (PICA)
Version 1.0.1

Please see http://kiwi.cs.dal.ca/Software/PICA for an up-to-date version of this document.

Norman MacDonald (norman@cs.dal.ca)

Phenotype Investigation with Classification Algorithms (PICA) is a Python framework for testing genotype-phenotype association algorithms.

Release Notes
Version 1.0.1
   - Updated documentation   

License
PICA is released under the  [http://creativecommons.org/licenses/by-sa/3.0/ Creative Commons Share-Alike Attribution 3.0 License].

Downloads
Example genotype dataset was compiled from the [http://www.string-db.org/ STRING database] version 8.0.  Example phenotype data is from the [http://img.jgi.doe.gov/cgi-bin/pub/main.cgi DOE JGI IMG] and [http://www.ncbi.nlm.nih.gov/genomes/lproks.cgi NCBI lproks].  Example taxonomic data is from the [http://www.ncbi.nlm.nih.gov/Taxonomy/ NCBI Taxonomy] database.

* [[Media:PICA_v1_00.zip|PICA v1.00]] PICA source code and example datasets

Setup
[http://www.python.org/ Python 2.6] and a suitable version of [http://numpy.scipy.org/ NumPy] for Python 2.6 are required.  [http://www.csie.ntu.edu.tw/~cjlin/libsvm/ LIBSVM] is required for the SVM training and testing plugins.

Unzip the folder to the desired location and run from the command line.  To access the API, make sure the pica folder is on your Python path.

Input data file format 
Input to PICA consists of two files, the samples/features file, and the class label file.  

The samples file is a tab-separated format without a header line.  Each line is a single sample, with the sample identifier in the first column.  The rest of the line are features for input.
Example:
  Escherichia_coli_CFT07                COG0007	COG0006	COG0004	COG0005	COG0001 ...	   
  Streptococcus_pyogenes_str._Manfredo	COG0005	COG0006	COG0008	COG0009	COG0010 ...
  ...
The features and samples can be in any order.

The class label file is a standard tab separated format.  A header line is required.  The first column must contain sample identifiers that map to the samples file. Not all class label lines must map to a sample.  This allows us to use a single class label file for all classes and possible training testing subsets of the genotype file.  To exclude a sample from a given class analysis, set the column value to NULL.
Example:
  organism	                       MOTILE  HALO  GRAMNEGATIVE ...
  Escherichia_coli_CFT07                YES     NULL  YES
  Streptococcus_pyogenes_str._Manfredo  NULL    NO    NULL
  ...


Output file format

The output tab-delimited rules file consists of an antecedent (also known as the body) of the rule and the consequent (also known as the head) of the rule.  Each antecedent is a comma separated list of features that are associated with the consequent. The consequent matches a class label in the input classes file.  The last column is the accuracy measure used by CPAR, Laplace accuracy, which is (1-Laplace error estimate) = (n+1) /(N+k), where N is the number of samples, n is the number of samples that contain the antecedent, and k is the number of distinct class labels.

Example:
  antecedent	consequent	laplace
  COG0568,COG2885,COG0756	NO	0.991150442478
  COG1651,COG1560	NO	0.990990990991
  COG1974,COG0132	NO	0.990990990991

  
  
Command-line Interface
Use the option -h for help with any command.

* train: Train a given data mining algorithm and output model to file.
Example usage:
  python train.py --algorithm cpar.CPARTrainer 
                  --samples examples/genotype_prokaryote.profile 
                  --classes examples/phenotype.profile 
                  --targetclass THERM 
                  --output output.rules 

* test:  Test a model with a classification algorithm and given model.
Example usage:
  python test.py --algorithm cpar.CPARClassifier 
                 --samples examples/genotype_prokaryote.profile 
                 --classes examples/phenotype.profile 
                 --targetclass THERM 
                 --model_filename output.rules 
                 --model_accuracy laplace

* crossvalidate:  Replicated cross-validation with the given training and testing algorithms.
Example usage:
  python crossvalidate.py --training_algorithm cpar.CPARTrainer 
                          --classification_algorithm cpar.CPARClassifier 
                          --accuracy_measure laplace
                          --replicates 10 
                          --folds 5 
                          --samples examples/genotype_prokaryote.profile 
                          --classes examples/phenotype.profile 
                          --targetclass THERM 
                          --output_filename results.txt 
                          --metadata examples/taxonomic_confounders_propagated.txt

Another example of crossvalidate is to use the CPAR2SVMTrainer, which trains with CPAR, then breaks down the rules found into individual features and subsequently trains and tests with LIBSVM.  This could also be performed more generally (with feature selection as a separate step) using the Python API below.

  python crossvalidate.py --training_algorithm cpar.CPAR2SVMTrainer 
                          --classification_algorithm libsvm.libSVMClassifier
                          --replicates 10 
                          --folds 5 
                          --samples examples/genotype_prokaryote.profile 
                          --classes examples/phenotype.profile 
                          --targetclass THERM 
                          --output_filename results.txt 
                          --metadata examples/taxonomic_confounders_propagated.txt

Python API 
Shortened example of a paired test between mutual information and conditionally weighted mutual information using the CWMIRankFeatureSelector class and the LIBSVM interface for testing each set of features.

See util/batch_validate.py for more details on an example of setting up a programmatic comparison.
  
  # Create an array to hold paired comparison configurations.
  test_configurations = []
  
  # Create the basic LIBSVM trainer and classifier 
  # that we will use to validate our feature selection.
  trainer = libSVMTrainer()
  classifier = libSVMClassifier()
  
  # Create two test configurations one for feature selection with mutual
  # information, the other with conditionally weighted mutual information.
  for score in ("mi","cwmi"):
      feature_selector = CWMIRankFeatureSelector(confounders_filename=confounders_filename,
                                                 scores=(score,),
                                                 features_per_class=10,
                                                 confounder="order")
      
      tc = TestConfiguration(score,feature_selector,trainer,classifier)
      test_configurations.append(tc)
  
  # Set up the crossvalidation class for 10 replicates of 5-fold cross-validation
  # and output the model from each replicate/fold to file name patterns starting
  # with 'root_output'.
  crossvalidator = CrossValidation(samples=samples,
                                   parameters=None,
                                   replicates=10,
                                   folds=5,
                                   test_configurations=test_configurations,
                                   root_output=root_output)
  
  # After cross-validation, the crossvalidator object holds the results of 
  # the paired comparisons that can be accessed through its methods. 
  crossvalidator.crossvalidate()


Contact Information

PICA is in active development and we are interested in discussing all potential applications of this software. We encourage you to send us suggestions for new features. Suggestions, comments, and bug reports can be sent to Rob Beiko (beiko [at] cs.dal.ca). If reporting a bug, please provide as much information as possible and a simplified version of the data set which causes the bug. This will allow us to quickly resolve the issue. 

Funding

The development and deployment of PICA has been supported by several organizations:

* [http://www.genomeatlantic.ca Genome Atlantic]
* The Dalhousie Centre for Comparative Genomics and Evolutionary Bioinformatics, and the [http://www.tula.org/ Tula Foundation]
* [http://www.nserc.ca The Natural Sciences and Engineering Research Council of Canada]
* The Dalhousie [http://cs.dal.ca Faculty of Computer Science]

