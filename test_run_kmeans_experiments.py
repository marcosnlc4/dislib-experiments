import time

import dislib as ds
import numpy as np
from dislib.cluster import KMeans

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

# # CLEAN CODE (FOR TRACE GENERATION)
    input_matrix_rows = 18
    input_matrix_columns = 10
    start_random_state = 170
    block_row_size = 3
    block_column_size = 10
    n_clusters = 10

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    start = time.perf_counter()
    # # CPU COLD
    # x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=1, id_cache=1)
    # # GPU COLD
    # x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=2, id_cache=1)
    # # CPU HOT
    # x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=1, id_cache=2)
    # GPU HOT
    x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=2, id_cache=2)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
    # arr = np.random.rand(input_matrix_rows, input_matrix_columns)
    # x = ds.array(arr, block_size=(block_row_size, block_column_size))

    # x_np = np.random.random(shape)
    # x = ds.array(x_np, block_size=block_size)
    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # print("\nSTART CPU COLD\n")
        # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1, id_cache=1, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # compss_barrier()
        # # print("==== TIME CPU ==== ", time.perf_counter()-start)
        # print("\END CPU COLD\n")

        # print("\nSTART GPU COLD\n")
        # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, id_cache=1, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # compss_barrier()
        # # print("==== TIME CPU ==== ", time.perf_counter()-start)
        # print("\END GPU COLD\n")

        # print("\nSTART CPU HOT\n")
        # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1, id_cache=2, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # compss_barrier()
        # # print("==== TIME CPU ==== ", time.perf_counter()-start)
        # print("\END CPU HOT\n")

        print("\nSTART GPU HOT\n")
        compss_barrier()
        # start = time.perf_counter()
        kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, id_cache=2, max_iter=5, tol=0, arity=48)
        kmeans.fit(x)
        compss_barrier()
        # print("==== TIME CPU ==== ", time.perf_counter()-start)
        print("\END GPU HOT\n")