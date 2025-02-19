The miner-subtypes tool
=========================

This utility generates sample subtype and related plots

You can see the tool's available options when you enter ``miner-subtypes -h``
at the command prompt:

.. highlight:: none

::

    usage: miner-subtypes [-h] expfile mapfile regulons outdir

    miner-subtypes - MINER compute sample subtypes

    positional arguments:
      expfile     input matrix
      mapfile     identifier mapping file
      regulons    regulons.json file from miner-mechinf
      outdir      output directory

    optional arguments:
      -h, --help  show this help message and exit


Parameters in detail
--------------------

``miner-subtypes`` expects at least these 4 arguments:

  * **expfile:** The gene expression file a matrix in csv format.
  * **mapfile:** The gene identifier map file.
  * **regulons:** The regulons.json file generated by the miner-mechinf tool.
  * **outdir:** The directory where the result files will be placed in.

Output in detail
----------------

After successful completion there will be the following files in the output directory

  * ``binaryActivityMap.pdf``
  * ``regulon_activity_heatmap.pdf``
  * ``centroid_clusters_heatmap.pdf``
  * ``regulons_activity_heatmap.csv``
  * ``centroidClusters_regulons.pdf``
  * ``similarityMatrix_regulons.pdf``
  * ``centroids.csv``
  * ``states_regulons_0o2_tsne.pdf``
  * ``eigengenes.csv``
  * ``transcriptional_programs_coexpressionModules`` - transcriptional programs
  * ``labeled_tsne_kmeans.pdf``
  * ``transcriptional_programs_vs_samples.pdf``
  * ``labeled_tsne_states.pdf``
  * ``tsne_gene_expression.pdf``
  * ``programs_vs_states.pdf``
  * ``tsne_regulon_activity.pdf``
