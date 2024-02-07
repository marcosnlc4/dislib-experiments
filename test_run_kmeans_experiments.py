import time

import dislib as ds
import numpy as np
from dislib.cluster import KMeans

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

# # CLEAN CODE (FOR TRACE GENERATION)
    input_matrix_rows = 12500
    input_matrix_columns = 100
    start_random_state = 170
    block_row_size = 3125
    block_column_size = 100
    n_clusters = 10

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    start = time.perf_counter()
    # CPU
    x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=1)
    # # GPU
    # x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=2)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
    # arr = np.random.rand(input_matrix_rows, input_matrix_columns)
    # x = ds.array(arr, block_size=(block_row_size, block_column_size))

    # x_np = np.random.random(shape)
    # x = ds.array(x_np, block_size=block_size)
    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # # Run KMeans using dislib - CPU
        # print("\nSTART CPU 3\n")
        # # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=3, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # # compss_barrier()
        # # print("==== TIME CPU ==== ", time.perf_counter()-start)
        # print("\END CPU 3\n")

        # print("\nSTART CPU 5\n")
        # # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=5, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # # compss_barrier()
        # # print("==== TIME CPU ==== ", time.perf_counter()-start)
        # print("\END CPU 5\n")

        print("\nSTART CPU 1\n")
        compss_barrier()
        # start = time.perf_counter()
        kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1, max_iter=5, tol=0, arity=48)
        kmeans.fit(x)
        compss_barrier()
        # print("==== TIME CPU ==== ", time.perf_counter()-start)
        print("\END CPU 1\n")


        # # Run KMeans using dislib - GPU
        # print("\nSTART GPU 4\n")
        # # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=4, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # # compss_barrier()
        # # print("==== TIME GPU ==== ", time.perf_counter()-start)
        # print("\END GPU 4\n")

        # print("\nSTART GPU 6\n")
        # # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=6, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # # compss_barrier()
        # # print("==== TIME GPU ==== ", time.perf_counter()-start)
        # print("\END GPU 6\n")

        # print("\nSTART GPU 2\n")
        # compss_barrier()
        # # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # compss_barrier()
        # # print("==== TIME GPU ==== ", time.perf_counter()-start)
        # print("\END GPU 2\n")