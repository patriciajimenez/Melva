# Strategies.py

import math

from deap import tools
from deap import algorithms


def eaMuPlusLambdaEarlyStop(
        population, toolbox, mu, lambda_, cxpb, mutpb, ngen,
        stats=None, halloffame=None, verbose=__debug__):
    """
        See the documentation regarding :class:`~deap.algorithms.eaMuPlusLambdaEarlyStop`.
        This strategy uses the `earlystop' callable in the toolbox to determine if
        the evolution must stop before the last generation is reached.
    """

    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats is not None else {}
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    gen = 0
    winner = toolbox.select(population, 1)[0]
    earlystop = toolbox.earlystop()
    while gen < ngen and not earlystop(winner):
        # Vary the population
        offspring = algorithms.varOr(population, toolbox, lambda_, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Select the next generation population
        population[:] = toolbox.select(population + offspring, mu)
        winner = toolbox.select(population, 1)[0]

        # Update the statistics with the new population
        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)
        gen += 1

    return population, logbook