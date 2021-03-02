# melva.py

import math
import numpy
import random
import pandas

from deap import creator, base, tools
from deap.algorithms import  eaMuPlusLambda
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score

from DiskCache import DiskCache
from WorkerManager import WorkerManager
from Strategies import eaMuPlusLambdaEarlyStop
from MelvaIndividual import MelvaIndividual
from MelvaEarlystop import MelvaEarlystop
from BaseClustererFactory import BaseClustererFactory


class Clusterer:

    # Constructor -------------------------------------------------------------

    # The weights are (k, silhouette, davies-bouldin, calinski-carabasz)
    creator.create("FitnessMax", base.Fitness, weights=(-1.00, +1.00, -1.00, +1.00))
    creator.create("Individual", MelvaIndividual, fitness=creator.FitnessMax, number_attributes=None)

    def __init__(self, configuration):
        self.cache = DiskCache()
        WorkerManager.cache = self.cache

        self.CXPB = configuration["CXPB"]
        self.MUTPB = configuration["MUTPB"]
        self.NGEN = configuration["NGEN"]
        self.PSIZE = configuration["PSIZE"]
        self.MU = math.ceil(configuration["MU"] * configuration["PSIZE"])
        self.LAMBDA = math.ceil(configuration["LAMBDA"] * configuration["PSIZE"])
        self.NCLU = configuration["NCLU"]
        self.BCLU = configuration["BCLU"]
        self.ES = configuration["ES"]

    # Business methods --------------------------------------------------------

    def fit(self, dataframe):
        if isinstance(dataframe, pandas.DataFrame):
            self.dataframe = dataframe
            original_dataframe = True
        else:
            assert isinstance(dataframe, list)
            assert isinstance(dataframe[0], list)
            self.dataframe = pandas.DataFrame(data=dataframe)
            original_dataframe = False

        self.number_data = self.dataframe.shape[0]
        self.number_attributes = len(self.dataframe.columns)

        toolbox = base.Toolbox()
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", self.mate)
        toolbox.register("mutate", self.mutate)
        toolbox.register("select", self.select)
        toolbox.register("generate_individual", creator.Individual, number_centroids=self.NCLU, number_data=self.number_data, number_attributes=self.number_attributes)
        toolbox.register("generate_population", tools.initRepeat, list, toolbox.generate_individual, self.PSIZE)
        toolbox.register("map", WorkerManager.map)
        toolbox.register("earlystop", MelvaEarlystop, tolerance=self.ES)

        population = toolbox.generate_population()
        offspring, _ = eaMuPlusLambdaEarlyStop(
            population=population,
            toolbox=toolbox,
            ngen=self.NGEN,
            cxpb=self.CXPB,
            mutpb=self.MUTPB,
            mu=self.MU,
            lambda_=self.LAMBDA,
            verbose=False
        )
        winners = tools.selBest(offspring, k=1)
        self.winner = winners[0]

        (hit, value) = self.cache.get(self.winner)
        assert hit
        self.number_centroids = value["number_centroids"]
        self.labels = value["labels"]
        self.labels_ = value["labels"]

        # INFO: quick and dirty!  This is to integrate Melva into TOMATE
        if original_dataframe:
            result = {
                "number_centroids": self.number_centroids,
                "selection_ratio": self.winner.selection_ratio(),
                "labels": self.labels.astype(numpy.int),
            }
        else:
            result = self

        #print(f"DATAFRAME = {self.number_data} x {self.number_attributes}")
        #print(f"labels = {len(self.labels_)} x 1")
        assert self.number_data == len(self.labels)

        return result

    # Ancillary methods -------------------------------------------------------

    def generate_individual(self, number_attributes):
        result = MelvaIndividual(number_attributes)

        return result

    def evaluate(self, individual):
        result = (math.inf, -math.inf, math.inf, -math.inf)
        labels = []

        attribute_indices = [i for i in range(0, len(individual.attribute_flags)) if individual.attribute_flags[i] == 1]

        if attribute_indices:
            projection = self.dataframe.iloc[:, attribute_indices]
            # TODO: find out if deduplicate returns a view, to avoid creating another dataset (inplace=True)
            deduplication = projection.drop_duplicates(inplace=False)
            number_data = deduplication.shape[0]

            if number_data >= individual.number_centroids:
                configuration = { "NCLU": individual.number_centroids }
                clusterer = BaseClustererFactory.create(self.BCLU, "Clusterer", configuration)
                number_centroids = clusterer.fit(deduplication)
                labels = clusterer.predict(projection)
                number_labels = len(set(labels))

                if number_centroids == number_labels and number_centroids >= 2:
                    result = (
                        number_centroids,
                        silhouette_score(projection, labels),
                        davies_bouldin_score(projection, labels),
                        calinski_harabasz_score(projection, labels)
                    )
                elif number_centroids == 1:
                    result = (1, -1.00, math.inf, 0.00)

        value = {
            "number_centroids": result[0],
            "silhouette_score": result[1],
            "davies_bouldin_score": result[2],
            "calinski_harabasz_score": result[3],
            "number_labels": len(set(labels)),
            "labels": labels
        }
        self.cache.put(individual, value)

        return result

    def mate(self, individual1, individual2):
        individual1.number_centroids, individual2.number_centroids = individual2.number_centroids, individual1.number_centroids,
        tools.cxOnePoint(individual1.attribute_flags, individual2.attribute_flags)

        return individual1, individual2

    def select(self, population, size):
        result = tools.selLexicase(population, size)

        return result

    def mutate(self, individual):
        if individual.auto_clustering:
            alpha = individual.number_centroids - 1 if individual.number_centroids > 2 else individual.number_centroids
            beta = individual.number_centroids + 1 if individual.number_centroids < individual.number_data // 2 else individual.number_centroids
            individual.number_centroids = random.randint(alpha, beta)
        tools.mutFlipBit(individual.attribute_flags, indpb=self.MUTPB)

        return (individual, )
