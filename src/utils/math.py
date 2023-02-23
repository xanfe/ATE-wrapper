import numpy as np


def sum_tuples(tuples):
    vector = np.zeros(shape=(2), dtype=int)
    for tuple_ in tuples:
        vector += np.asarray(tuple_)
    return tuple(vector)