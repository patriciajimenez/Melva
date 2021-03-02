# agglomerative-ward.py

import warnings

from sklearn import cluster


class AgglomerativeClusterer:

    def __init__(self, configuration, linkage):
        self.configuration = configuration
        self.model = None
        self.linkage = linkage

    def fit(self, dataset):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            requested_n_clusters = self.configuration["NCLU"]
            engine = cluster.AgglomerativeClustering(n_clusters=requested_n_clusters, linkage=self.linkage)
            self.model = engine.fit(dataset)
            fitted_n_clusters = self.model.n_clusters_
            if fitted_n_clusters < requested_n_clusters:
                # INFO: Ward must have issued a warning
                result = fitted_n_clusters
            else:
                result = requested_n_clusters

        return result

    def predict(self, dataset):
        result = self.model.fit_predict(dataset)

        return result
