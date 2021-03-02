# MelvaIndividual.py

import math
import random
import hashlib


class MelvaIndividual:

    def __init__(self, number_centroids, number_data, number_attributes):
        assert number_centroids == 0 or 2 <= number_centroids <= number_data
        assert number_data >= 2
        assert number_attributes >= 2

        if number_centroids >= 2:
            self.number_centroids = number_centroids
            self.auto_clustering = False
        else:
            #rnd = math.ceil(0.10 * number_data)
            rnd = math.ceil(math.sqrt(number_data))
            if rnd <= 2:
                self.number_centroids = 2
            else:
                self.number_centroids = random.randint(2, rnd)
            self.auto_clustering = True
        self.number_data = number_data
        self.number_attributes = number_attributes

        self.attribute_flags = [0]
        while all(not flag for flag in self.attribute_flags):
            self.attribute_flags = [random.randint(0, 1) for _ in range(number_attributes)]

    def selection_ratio(self):
        result = sum(self.attribute_flags) / self.number_attributes

        return result

    def hash(self):
        key = f"{self.number_centroids:010}/" + "".join([str(a) for a in self.attribute_flags])
        bytes = key.encode()
        result = hashlib.md5(bytes).hexdigest()

        return result

    def __str__(self):
        result = f"(S={round(self.fitness.values[0], 2) if self.fitness.valid else None}, " + \
                 f"DB={round(self.fitness.values[1], 2) if self.fitness.valid else None}, " + \
                 f"HC={round(self.fitness.values[2], 2) if self.fitness.valid else None}, " + \
                 f"k={self.number_centroids}, " + \
                 f"A={self.attribute_flags})"

        return result
