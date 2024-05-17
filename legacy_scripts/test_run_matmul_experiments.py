import time
import csv
import dislib as ds
import numpy as np
from scipy import sparse as sp
from scipy.sparse import csr_matrix

from pycompss.api.api import compss_barrier

if __name__ == '__main__':


    input_matrix_rows = 40
    input_matrix_columns = 40
    start_random_state = 170
    block_row_size = 10
    block_column_size = 10
    transpose_a = transpose_b = bl_transpose = False
    start = time.perf_counter()

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    # DATASET GENERATION
    # start = time.perf_counter()
    # x = ds.random_array(shape, block_size, random_state=start_random_state)
    # print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    x_np = np.random.random(shape)
    x = ds.array(x_np, block_size=block_size)

    
    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # Run Matmul using dislib - CPU
        print("\nSTART CPU\n")
        # compss_barrier()
        # start = time.perf_counter()
        result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=0, nr_algorithm_iteration=0)
        # compss_barrier()
        # print("==== TIME CPU ==== ", time.perf_counter()-start)
        print("\END CPU\n")
        

        ## Run Matmul using dislib - GPU 
        #print("\nSTART GPU\n")
        #compss_barrier()
        #start = time.perf_counter()
        #result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)
        #compss_barrier()
        #print("==== TIME GPU ==== ", time.perf_counter()-start)