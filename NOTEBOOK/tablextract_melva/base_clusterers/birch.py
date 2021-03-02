# birch.py

import warnings

from sklearn import cluster


class Clusterer:

    def __init__(self, configuration):
        self.configuration = configuration
        self.model = None

    def fit(self, dataset):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            requested_n_clusters = self.configuration["NCLU"]
            engine = cluster.Birch(n_clusters=requested_n_clusters)
            self.model = engine.fit(dataset)
            fitted_n_clusters = len(self.model.subcluster_centers_)
            if fitted_n_clusters < requested_n_clusters:
                # INFO: Birch must have issued a warning
                result = fitted_n_clusters
            else:
                result = requested_n_clusters

        return result

    def predict(self, dataset):
        result = self.model.predict(dataset)

        return result
