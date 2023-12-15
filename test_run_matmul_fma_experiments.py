import time
import csv
import dislib as ds
import numpy as np

from pycompss.api.api import compss_wait_on

if __name__ == '__main__':

    input_matrix_rows = 4
    input_matrix_columns = 4
    start_random_state = 170
    block_row_size = 2
    block_column_size = 2
    transpose_a = transpose_b = bl_transpose = False
    
    num_blocks = int(input_matrix_rows/block_row_size) #grid_row_size
    elems_per_block = block_row_size

    # DATASET GENERATION
    start = time.perf_counter()
    # Generate the dataset in a distributed manner
    # i.e: avoid having the master a whole matrix
    A, C = [], []
    matrix_name = ["A"]
    for i in range(num_blocks):
        for l in [A, C]:
            l.append([])
        # Keep track of blockId to initialize with different random seeds
        bid = 0
        for j in range(num_blocks):
            for ix, l in enumerate([A]):
                l[-1].append(ds.generate_block(elems_per_block,
                                            num_blocks,
                                            random_state=start_random_state,
                                            bid=bid))
                bid += 1
            C[-1].append(ds.generate_block(elems_per_block,
                                        num_blocks,
                                        set_to_zero=True))
    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    #TEST INPUTS
    # print('A')
    # A_print = A.copy()
    # print(compss_wait_on(A_print))

    # print('C before')
    # C_print = C.copy()
    # print(compss_wait_on(C_print))

    nr_iterations = 0
    
    for i in range(nr_iterations + 1):

        # Run Matmul using dislib - CPU
        print("\nSTART CPU\n")
        # compss_barrier()
        # start = time.perf_counter()
        ds.dot(A, A, C, id_device=6, id_parameter=0, nr_algorithm_iteration=0)
        # compss_barrier()
        # print("==== TIME CPU ==== ", time.perf_counter()-start)
        print("\END CPU\n")
        
        #TEST OUTPUTS
        print('C after')
        print(compss_wait_on(C))
        
        ## Run Matmul using dislib - GPU 
        #print("\nSTART GPU\n")
        #compss_barrier()
        #start = time.perf_counter()
        #ds.dot(A, A, C, id_device=1, id_parameter=0, nr_algorithm_iteration=0)
        #compss_barrier()
        #print("==== TIME GPU ==== ", time.perf_counter()-start)