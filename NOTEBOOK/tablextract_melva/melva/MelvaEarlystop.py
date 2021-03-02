# MelvaEarlystop.py

import math
import numpy
import random
import pandas
import hashlib

from deap import creator, algorithms, base, tools
from sklearn import cluster
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score

from MelvaIndividual import MelvaIndividual
from DiskCache import DiskCache
from WorkerManager import WorkerManager


class MelvaEarlystop:

    # Constructor -------------------------------------------------------------

    def __init__(self, tolerance):
        self.tolerance = tolerance
        self.old_fitness = None # (-1.00 k, +1.00 silhouette, -1.00 davies-bouldin, +1.00 calinski-carabasz)
        self.stuck = 0

    # Core methods ------------------------------------------------------------

    def __call__(self, winner):
        new_fitness = winner.fitness.values
        assert new_fitness is not None

        if self.old_fitness is None:
            result = False
        else:
            silhouette_delta = new_fitness[1] - self.old_fitness[1]
            davies_bouldin_delta = new_fitness[2] - self.old_fitness[2]
            calinski_harabasz_delta = new_fitness[3] - self.old_fitness[3]
            improvement = silhouette_delta > 0.00 or davies_bouldin_delta < 0.00 or calinski_harabasz_delta > 0.00
            if not improvement:
                self.stuck += 1
            else:
                self.stuck = 0
            result = (self.stuck == self.tolerance)

        self.old_fitness = new_fitness

        return result
