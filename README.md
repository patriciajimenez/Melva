# Melva

This repository provides everything you need to repeat the experimentation regarding the following article:

	A Genetic Clustering Approach to Extract Data from HTML Tables
	Patricia Jiménez, Juan C. Roldán, Rafael Corchuelo
	Submitted to Information Processing & Management


DATA
----

This folder provides the full repository used to perform the experimentation.  It has the following sub-folders:

- nishida: this folder provides the experimental tables in a format that is amenable to be used with Nishida et. al.'s proposal.
- original_tables: this folder provides the experimental tables in a format that is amenable to be used with the other proposals.
- tomate: this folder has some meta-data that are used for validation purposes.  The annotation tool is available at http://tomatera.tdg-seville.info.

There are also some additional files: 

- Cambria2.ttf: this is the font used in the notebook; installing it is optional.
- enwiki_20180420_100d.txt: this are the embeddings computed to experiment with Nishida et. al.'s proposal.
- text-metadata-dict.pk: this is a dictionary with meta-data about the tables used in the experimentation.

NOTEBOOK
--------

This folder provides the notebook that we prepared to perform the experimentation.  Before you run it for the first time, we recommend that you should:

- Create a conda environment called "melva" in which you must install Python 3.7
- Activate the "melva" environment.
- Install the dependencies by means of command "pip install -r requirements.txt"

To launch the experimentation environment, please, run command "launch.cmd" in Windows and "./launch.sh" in Linux.  This will open the folder in Jupyter.  Please, select the notebook called "Experimental-Analysis.ipynb" and follow the instructions therein.
