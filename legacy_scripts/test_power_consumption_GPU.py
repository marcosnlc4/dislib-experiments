import subprocess
import time
import dislib as ds
import cupy as cp

# Function to measure GPU power consumption before and after running a function
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
    
    # Get initial GPU power usage
    initial_power_usage = get_gpu_power_usage()

    # Run the function of interest
    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)

    # Get final GPU power usage
    final_power_usage = get_gpu_power_usage()

    print(initial_power_usage)
    print("\n\n")
    print(final_power_usage)

    # Calculate the estimated power consumption difference
    power_consumption = final_power_usage - initial_power_usage

    print(f"Estimated GPU Power Consumption: {power_consumption:.2f} Watts")

# Function to get GPU power usage using nvidia-smi
def get_gpu_power_usage():
    try:
        power_output = subprocess.check_output(
            "nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits",
            shell=True,
            stderr=subprocess.STDOUT,
        )
        power_usage = power_output.strip()
        return power_usage
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output.decode('utf-8')}")
        return 0.0

# Example: Measure GPU power consumption while running the CuPy function
measure_power_consumption()