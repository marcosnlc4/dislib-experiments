import pyRAPL
import time
import dislib as ds
import numpy as np

# Function to measure CPU power consumption before and after running a function
def measure_power_consumption():
    
    input_matrix_rows = 4000
    input_matrix_columns = 4000
    start_random_state = 170
    block_row_size = 1000
    block_column_size = 1000
    transpose_a = transpose_b = False

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    x = ds.random_array(shape, block_size, random_state=start_random_state)
    
    pyRAPL.setup()
    measure = pyRAPL.Measurement('bar')
    measure.begin()

    # Run the function of interest
    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=0, nr_algorithm_iteration=0)

    measure.end()

    print((measure.result.pkg[0])/measure.result.duration)

# Example: Measure CPU power consumption while running the numpy function
measure_power_consumption()