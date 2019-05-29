import sys,os,dill,numpy
import matplotlib,matplotlib.pyplot

matplotlib.rcParams.update({'font.size':18,'font.family':'Arial','xtick.labelsize':14,'ytick.labelsize':14})
matplotlib.rcParams['pdf.fonttype']=42

import miner2
import miner2.preprocess
import miner2.coexpression
import miner2.mechanisticInference

# 0.0. user defined variables
expression_file='/Volumes/omics4tb2/alomana/projects/miner2/data/IA12Zscore.csv'
results_dir='/Volumes/omics4tb2/alomana/projects/miner2/results/IA12Zscore/'

num_cores = 8         # required for coexpression
min_number_genes = 6   # required for coexpression
min_correlation = 0.2 # required for mechanistic inference. Bulk RNAseq default=0.2;single cell RNAseq default=0.05

# 0.1. build results directory tree
if os.path.exists(results_dir) == False:
    os.mkdir(results_dir)
    os.mkdir(results_dir+'figures')
    os.mkdir(results_dir+'info')

# use as needed
# dill.dump_session(results_dir+'info/bottle.dill')
# dill.load_session(results_dir+'info/bottle.dill')

# STEP 0: load the data
expression_data, conversion_table = miner2.preprocess.main(expression_file)

individual_expression_data = [expression_data.iloc[:,i] for i in range(50)]
matplotlib.pyplot.boxplot(individual_expression_data)
matplotlib.pyplot.title("Patient expression profiles")
matplotlib.pyplot.ylabel("Relative expression")
matplotlib.pyplot.xlabel("Sample ID")
matplotlib.pyplot.xticks(fontsize=6)

figureName=results_dir+'figures/boxplots.pdf'
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(figureName)
matplotlib.pyplot.clf()

matplotlib.pyplot.hist(expression_data.iloc[0,:],bins=100,alpha=0.75)
matplotlib.pyplot.title("Expression of single gene")
matplotlib.pyplot.ylabel("Frequency")
matplotlib.pyplot.xlabel("Relative expression")

figureName=results_dir+'figures/singleGene.pdf'
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(figureName)
matplotlib.pyplot.clf()

matplotlib.pyplot.hist(expression_data.iloc[:,0],bins=200,color=[0,0.4,0.8],alpha=0.75)
matplotlib.pyplot.ylim(0,350)
matplotlib.pyplot.title("Expression of single patient sample",FontSize=14)
matplotlib.pyplot.ylabel("Frequency")
matplotlib.pyplot.xlabel("Relative expression")

figureName=results_dir+'figures/singlePatient.pdf'
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(figureName)
matplotlib.pyplot.clf()

# STEP 1: clustering
initial_clusters = miner2.coexpression.cluster(expression_data,min_number_genes=min_number_genes,num_cores=num_cores)
revised_clusters = miner2.coexpression.reviseInitialClusters(initial_clusters,expression_data)

sys.exit()

# QC: visualize coexpression clusters

# retrieve first 10 clusters for visual inspection
first_clusters = numpy.hstack([revisedClusters[i] for i in numpy.arange(10).astype(str)])
# visualize first 10 clusters
matplotlib.pyplot.imshow(expressionData.loc[first_clusters,:],aspect="auto",cmap="viridis",vmin=-1,vmax=1)
matplotlib.pyplot.grid(False)
matplotlib.pyplot.ylabel("Genes")
matplotlib.pyplot.xlabel("Samples")
matplotlib.pyplot.title("First 10 coexpression clusters")
figureName=resultsDir+'figures/first.coexpression.clusters.pdf'
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(figureName)
matplotlib.pyplot.clf()
# visualize 10 random clusters
matplotlib.pyplot.imshow(expressionData.loc[numpy.random.choice(expressionData.index,len(first_clusters),replace=False),:],aspect="auto",cmap="viridis",vmin=-1,vmax=1)
matplotlib.pyplot.grid(False)
matplotlib.pyplot.ylabel("Genes")
matplotlib.pyplot.xlabel("Samples")
matplotlib.pyplot.title("Random coexpression genes")
figureName=resultsDir+'figures/random.coexpression.clusters.pdf'
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(figureName)
matplotlib.pyplot.clf()

# STEP 2: mechanistic inference
dill.dump_session(resultsDir+'info/bottle.dill')
#dill.load_session(resultsDir+'info/bottle.dill')

# get first principal component axes of clusters
axes = miner2.mechanisticInference.principalDf(revisedClusters,expressionData,subkey=None,minNumberGenes=1)

# analyze revised clusters for enrichment in relational database 
mechanisticOutput = miner2.mechanisticInference.enrichment(axes,revisedClusters,expressionData,correlationThreshold=minCorrelation,numCores=numCores)

# order mechanisticOutput as {tf:{coexpressionModule:genes}} 
#coregulationModules = miner.getCoregulationModules(mechanisticOutput)

# get final regulons by keeping genes that requently appear coexpressed and associated to a common regulator
#regulons = miner.getRegulons(coregulationModules,minNumberGenes=minNumberRegulonGenes,freqThreshold = 0.333)

# reformat regulon dictionary for consistency with revisedClusters and coexpressionModules
#regulonModules, regulonDf = miner.regulonDictionary(regulons)

# define coexpression modules as composite of coexpressed regulons
#coexpressionModules = miner.getCoexpressionModules(mechanisticOutput)

# reconvert revised clusters to original gene annotations
#annotatedRevisedClusters = miner.convertDictionary(revisedClusters,conversionTable)

# reconvert results into original annotations
#regulonAnnotatedDf = miner.convertRegulons(regulonDf,conversionTable)

#reconvert regulons
#annotatedRegulons = miner.convertDictionary(regulonModules,conversionTable)

#reconvert coexpression modules
#annotatedCoexpressionModules = miner.convertDictionary(coexpressionModules,conversionTable)




