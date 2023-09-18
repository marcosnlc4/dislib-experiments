import subprocess
import time

# Function to measure GPU power consumption before and after running a function
def measure_power_consumption(func):
    # Get initial GPU power usage
    initial_power_usage = get_gpu_power_usage()

    # Run the function of interest
    func()

    # Get final GPU power usage
    final_power_usage = get_gpu_power_usage()

    print(initial_power_usage)
    print("\n\n")
    print(final_power_usage)

    # Calculate the estimated power consumption difference
    # power_consumption = final_power_usage - initial_power_usage

    # print(f"Estimated GPU Power Consumption: {power_consumption:.2f} Watts")

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

# Define a CuPy function (replace with your specific CuPy code)
import cupy as cp

def cupy_function():
    # Create a CuPy array and perform some operations
    x = cp.random.rand(1000, 1000)
    y = cp.dot(x, x.T)
    cp.cuda.Stream.null.synchronize()

# Example: Measure GPU power consumption while running the CuPy function
measure_power_consumption(cupy_function)
