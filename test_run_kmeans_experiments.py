import time

import dislib as ds
import numpy as np
from dislib.cluster import KMeans

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

# # CLEAN CODE (FOR TRACE GENERATION)
    input_matrix_rows = 8
    input_matrix_columns = 2
    start_random_state = 170
    block_row_size = 2
    block_column_size = 2
    n_clusters = 10

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    # CPU COLD
    id_device=1
    id_cache=1
    # # CPU HOT
    # id_device=1
    # id_cache=2
    # # GPU COLD
    # id_device=2
    # id_cache=1
    # # GPU HOT
    # id_device=2
    # id_cache=2

    start = time.perf_counter()
    x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=id_device, id_cache=id_cache)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
    # arr = np.random.rand(input_matrix_rows, input_matrix_columns)
    # x = ds.array(arr, block_size=(block_row_size, block_column_size))

    # x_np = np.random.random(shape)
    # x = ds.array(x_np, block_size=block_size)
    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        print("\nSTART\n")
        # compss_barrier()
        start = time.perf_counter()
        kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=id_device, id_cache=id_cache, max_iter=5, tol=0, arity=48)
        kmeans.fit(x)
        # compss_barrier()
        print("==== TIME ==== ", time.perf_counter()-start)
        print("\END\n")