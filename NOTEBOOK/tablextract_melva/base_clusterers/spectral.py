# spectral.py

import warnings
import numpy

from sklearn import cluster
from sklearn import metrics


class Clusterer:

    # Business methods --------------------------------------------------------

    def __init__(self, configuration):
        self.configuration = configuration

    def fit(self, dataset):
        requested_n_clusters = self.configuration["NCLU"]
        labels = self.do_cluster(dataset, requested_n_clusters)
        fitted_n_clusters = len(set(labels))
        if fitted_n_clusters < requested_n_clusters:
            result = fitted_n_clusters
        else:
            result = requested_n_clusters

        return result

    def predict(self, dataset):
        requested_n_clusters = self.configuration["NCLU"]
        result = self.do_cluster(dataset, requested_n_clusters)

        return result

    # Ancillary methods -------------------------------------------------------

    def do_cluster(self, dataset, n_clusters):
        distances = metrics.pairwise_distances(dataset, metric="euclidean")
        affinity = numpy.exp(-0.10 * distances / distances.std())
        result = cluster.spectral_clustering(affinity, n_clusters=n_clusters, eigen_solver='arpack', assign_labels="discretize")

        return result

