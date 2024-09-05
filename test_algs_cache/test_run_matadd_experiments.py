import time
import csv
import dislib as ds
import numpy as np
from scipy import sparse as sp
from scipy.sparse import csr_matrix

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

    input_matrix_rows = 20
    input_matrix_columns = 20
    start_random_state = 170
    block_row_size = 5
    block_column_size = 5
    transpose_a = transpose_b = bl_transpose = False
    start = time.perf_counter()

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

    # DATASET GENERATION
    start = time.perf_counter()
    x = ds.random_array(shape, block_size, random_state=start_random_state, id_device=id_device, id_cache=id_cache)
    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # Run Matmul using dislib - TEST CASES 
        print("\nSTART\n")
        # compss_barrier()
        start = time.perf_counter()
        result = ds.matadd(x, x, id_device=id_device, id_cache=id_cache, id_parameter=0, nr_algorithm_iteration=0)
        # compss_barrier()
        print("==== TIME ==== ", time.perf_counter()-start)