# kmeans.py

import numpy

from sklearn import cluster
from sklearn.metrics import silhouette_score


class Clusterer:

    def __init__(self, configuration):
        self.configuration = configuration
        self.model = None

    def fit(self, dataset):
        if dataset.shape[0] <= 1000:
            engine = cluster.KMeans(n_clusters=self.configuration["NCLU"], n_jobs=1)
        else:
            engine = cluster.MiniBatchKMeans(n_clusters=self.configuration["NCLU"], init_size=self.configuration["NCLU"])

        self.model = engine.fit(dataset)
        result = len(self.model.cluster_centers_)

        return result

    def predict(self, dataset):
        result = self.model.predict(dataset)

        return result