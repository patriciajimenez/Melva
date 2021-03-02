# agglomerative-ward.py

import warnings

from sklearn import cluster
from agglomerative import AgglomerativeClusterer


class Clusterer(AgglomerativeClusterer):

    def __init__(self, configuration):
        super().__init__(configuration, "ward")
