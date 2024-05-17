import time

import dislib as ds
import numpy as np
from dislib.decomposition import PCA

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

# # CLEAN CODE (FOR TRACE GENERATION)
    input_matrix_rows = 1250
    input_matrix_columns = 100
    start_random_state = 170
    block_row_size = 125
    block_column_size = 100
    n_clusters = 10

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    start = time.perf_counter()
    x = ds.random_array(shape, block_size, random_state=start_random_state)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # Run PCA using dislib - CPU (tasks: _subset_scatter_matrix(GPU), _merge_partial_scatter_matrix, _estimate_covariance, _decompose(GPU), _subset_transform(GPU))
        print("\nSTART CPU\n")
        pca = PCA(method='svd', arity=48)
        pca.fit(x)
        print("\END CPU\n")


        # # Run PCA using dislib - GPU
        # print("\nSTART GPU\n")
        # compss_barrier()
        # start = time.perf_counter()
        # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, max_iter=5, tol=0, arity=48)
        # kmeans.fit(x)
        # compss_barrier()
        # print("==== TIME GPU ==== ", time.perf_counter()-start)