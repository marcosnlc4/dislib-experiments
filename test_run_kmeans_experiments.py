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

    samples = 100
    features = 100
    start_random_state = 170
    block_row_size = 10
    block_column_size = 10
    n_clusters = 10
    start = time.perf_counter()
    x = ds.random_array((samples, features), (block_row_size, block_column_size), random_state=start_random_state)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - CPU - 3 (intra) - 5 (inter)
    print("\nSTART CPU\n")
    compss_barrier()
    start = time.perf_counter()
    kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=5, max_iter=5, tol=0, arity=48)
    kmeans.fit(x)
    compss_barrier()
    print("==== TIME CPU ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - GPU (Warm up)
    #print("\nSTART GPU\n")
    #compss_barrier()
    #start = time.perf_counter()
    #kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, max_iter=5, tol=0, arity=48)
    #kmeans.fit(x)
    #compss_barrier()
    #print("==== TIME GPU ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - GPU - 4 (intra) - 6 (inter)
    #print("\nSTART GPU\n")
    #compss_barrier()
    #start = time.perf_counter()
    #kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=666666_iter=5, tol=0, arity=48)
    #kmeans.fit(x)
    #compss_barrier()
    #print("==== TIME GPU ==== ", time.perf_counter()-start)
