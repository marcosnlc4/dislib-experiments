import dislib as ds
import numpy as np
import cupy as cp
from pycompss.api.parameter import COLLECTION_IN, Type, Cache
from pycompss.api.task import task

 
def function_cupy():
    return cp.add(x,x)

def function_numpy():
    return np.add(x,x)

@task(x={Type: COLLECTION_IN, Cache: True},returns=np.array, cache_returns=False)
def compss_task(x):
    for i in range(100):
        if i <= p_fraction*100:
            y = function_cupy(x)
        else:
            y = function_numpy(x)

    return y

def generate_dataset(input_matrix_rows, input_matrix_columns, block_row_size, block_column_size):
    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    return ds.random_array(shape, block_size, random_state=start_random_state, id_device=1)

if __name__ == '__main__':

    #inputs
    input_matrix_rows = 100
    input_matrix_columns = 100
    start_random_state = 170
    block_row_size = 10
    block_column_size = 10
    p_fraction = 0.8

    x = generate_dataset(input_matrix_rows, input_matrix_columns, block_row_size, block_column_size)
    
    for row in x._iterator(axis=0):
        artifact = compss_task(x)