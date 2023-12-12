import subprocess
import dislib as ds
from pycompss.api.api import compss_barrier

# Function to measure CPU power consumption in Watts
def measure_cpu_power(function_to_run):
    # Start monitoring CPU power using a tool like 'powerstat' (Linux-specific)
    cpu_power_process = subprocess.Popen(
        ["powerstat", "-R", "1"],  # Run 'powerstat' to monitor CPU power with a 1-second interval
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Run the function you want to monitor on the CPU
    function_to_run()

    # Stop the CPU power monitoring process
    cpu_power_process.terminate()

    # Process the power consumption data (output of 'powerstat')
    power_data = cpu_power_process.stdout.read()
    print("CPU Power Consumption:")
    print(power_data)

# Function to measure GPU power consumption in Watts
def measure_gpu_power(function_to_run):
    # Start monitoring GPU power using 'nvidia-smi'
    gpu_power_process = subprocess.Popen(
        ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits", "-l", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Run the function you want to monitor on the GPU
    compss_barrier()
    function_to_run()
    compss_barrier()

    # Stop the GPU power monitoring process
    gpu_power_process.terminate()

    # Process the power consumption data (output of 'nvidia-smi')
    power_data = gpu_power_process.stdout.read()
    print("GPU Power Consumption:")
    print(power_data)

# Example functions to run on CPU and GPU
def function_to_run_on_cpu():
    # Add CPU-bound workload here
    input_matrix_rows = 3200
    input_matrix_columns = 3200
    start_random_state = 170
    block_row_size = 100
    block_column_size = 100
    transpose_a = transpose_b = False

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    x = ds.random_array(shape, block_size, random_state=start_random_state)

    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=0, nr_algorithm_iteration=0)


def function_to_run_on_gpu():
    # Add GPU-bound workload here
    input_matrix_rows = 3200
    input_matrix_columns = 3200
    start_random_state = 170
    block_row_size = 100
    block_column_size = 100
    transpose_a = transpose_b = False

    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    x = ds.random_array(shape, block_size, random_state=start_random_state)

    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)

if __name__ == "__main__":
    print("Measuring CPU Power Consumption...")
    measure_cpu_power(function_to_run_on_cpu)

    print("\nMeasuring GPU Power Consumption...")
    measure_gpu_power(function_to_run_on_gpu)