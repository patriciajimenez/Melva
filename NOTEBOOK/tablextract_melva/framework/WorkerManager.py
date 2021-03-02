# WorkerManager.py

import multiprocessing
import math

from concurrent.futures import Future
from concurrent.futures import ProcessPoolExecutor


class WorkerManager:

    MULTIPLIER = 0.25
    CPU_COUNT = multiprocessing.cpu_count()

    @staticmethod
    def initialise():
        WorkerManager.NUM_WORKERS = min(max(1, math.ceil(WorkerManager.MULTIPLIER * WorkerManager.CPU_COUNT)), WorkerManager.CPU_COUNT)
        WorkerManager.pool = multiprocessing.Pool(WorkerManager.NUM_WORKERS)
        WorkerManager.executor = ProcessPoolExecutor(max_workers=WorkerManager.NUM_WORKERS)

    cache = None

    @staticmethod
    def map(handler, individuals): # This is V3
        num_data = len(individuals)
        chunk_size = max(1, math.ceil(num_data / WorkerManager.NUM_WORKERS))
        chunks = [individuals[i: i + chunk_size] for i in range(0, len(individuals), chunk_size)]
        num_chunks = len(chunks)

        local_futures = []
        for index, chunk in enumerate(chunks):
            for counter, individual in enumerate(chunk):
                (hit, value) = WorkerManager.cache.get(individual)
                if hit: chunk[counter] = None
            future = WorkerManager.executor.submit(WorkerManager.scatter, handler, chunk, index)
            local_futures.append(future)

        result = []
        for index, future in enumerate(local_futures):
            oops = future.exception()
            if oops: raise oops
            output = future.result()
            for counter, evaluation in enumerate(output):
                if evaluation is None:
                    (hit, value) = WorkerManager.cache.get(individuals[index + counter])
                    assert hit
                    output[counter] = (value["number_centroids"], value["silhouette_score"], value["davies_bouldin_score"], value["calinski_harabasz_score"])
            result.extend(output)

        return result

    @staticmethod
    def scatter(handler, chunk, index):
        result = []
        for datum in chunk:
            if datum is not None:
                output = handler(datum)
            else:
                # The result was pre-fetched from the cache
                output = None
            result.append(output)

        return result

    """
    # INFO: this is a simple implementation that is not as efficient as the previous one.
    @staticmethod
    def map(handler, data):
        num_data = len(data)
        chunk_size = max(1, math.ceil(num_data / WorkerManager.NUM_WORKERS))
        #result = WorkerManager.pool.map(handler, data) # This is V1
        result = WorkerManager.pool.map(handler, data, chunk_size) # This is V2

        return result
    """