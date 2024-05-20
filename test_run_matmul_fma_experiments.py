import time
import csv
import dislib as ds
import numpy as np

from pycompss.api.api import compss_wait_on
from pycompss.api.api import compss_barrier
from dataset_generator import generate_dataset

if __name__ == '__main__':

    input_matrix_rows = 4
    input_matrix_columns = 4
    start_random_state = 170
    block_row_size = 2
    block_column_size = 2
    grid_row_size = int(input_matrix_rows/block_row_size)
    grid_column_size = int(input_matrix_columns/block_column_size)

    transpose_a = transpose_b = bl_transpose = False
    
    num_blocks = int(input_matrix_rows/block_row_size) #grid_row_size
    elems_per_block = block_row_size

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
    A = generate_dataset(vl_dataset_row_dimension=input_matrix_rows, vl_dataset_column_dimension=input_matrix_columns, vl_block_row_dimension=block_row_size, vl_block_column_dimension=block_column_size, vl_grid_row_dimension=grid_row_size, vl_grid_column_dimension=grid_column_size, nr_random_state=start_random_state, vl_data_skewness=0.0, ds_algorithm="MATMUL_FMA", id_device=id_device, id_cache=id_cache)
    B = generate_dataset(vl_dataset_row_dimension=input_matrix_rows, vl_dataset_column_dimension=input_matrix_columns, vl_block_row_dimension=block_row_size, vl_block_column_dimension=block_column_size, vl_grid_row_dimension=grid_row_size, vl_grid_column_dimension=grid_column_size, nr_random_state=start_random_state, vl_data_skewness=0.0, ds_algorithm="MATMUL_FMA", id_device=id_device, id_cache=id_cache)
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
    
    # # TEST INPUTS
    # print('A')
    # A_print = A.copy()
    # print(compss_wait_on(A_print))

    # print('B')
    # B_print = B.copy()
    # print(compss_wait_on(B_print))

    # Generate empty output matrix C to receive the result of the multiplication
    num_blocks = grid_row_size
    elems_per_block = block_row_size

    C = []
    for i in range(num_blocks):
        for l in [C]:
            l.append([])
        # Keep track of blockId to initialize with different random seeds
        bid = 0
        for j in range(num_blocks):
            C[-1].append(ds.generate_block(elems_per_block,
                                        num_blocks,
                                        set_to_zero=True,
                                        id_device=id_device, id_cache=id_cache))

    # print('C')
    # C_print = C.copy()
    # print(compss_wait_on(C_print))
    
    nr_iterations = 0
    for i in range(nr_iterations + 1):

        # Run Matmul using dislib - CPU
        print("\nSTART\n")
        compss_barrier()
        # start = time.perf_counter()
        ds.dot(A, B, C, id_device=id_device, id_cache=id_cache, id_parameter=0, nr_algorithm_iteration=0)
        # compss_barrier()
        # print("==== TIME CPU ==== ", time.perf_counter()-start)
        print("\END\n")
        
        # #TEST OUTPUTS
        # print('C after')
        # print(compss_wait_on(C))