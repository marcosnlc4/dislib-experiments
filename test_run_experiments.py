import time

import dislib as ds
from dislib.cluster import KMeans

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

    # samples = 10
    # features = 10
    # start_random_state = 170
    # block_row_size = 2
    # block_column_size = 2
    # n_clusters = 10

    samples = 1000000000
    features = 10
    start_random_state = 170
    block_row_size = 1000000
    block_column_size = 10
    n_clusters = 50
    start = time.perf_counter()
    x = ds.random_array((samples, features), (block_row_size, block_column_size), random_state=start_random_state)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - CPU
    print("\nSTART CPU\n")
    compss_barrier()
    start = time.perf_counter()
    kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1, max_iter=5, tol=0, arity=48)
    kmeans.fit(x)
    compss_barrier()
    print("==== TIME CPU ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - GPU
    print("\nSTART GPU\n")
    compss_barrier()
    start = time.perf_counter()
    kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, max_iter=5, tol=0, arity=48)
    kmeans.fit(x)
    compss_barrier()
    print("==== TIME GPU ==== ", time.perf_counter()-start)