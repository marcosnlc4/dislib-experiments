import numpy as np
import time
import inspect
import matplotlib.pyplot as plt

# Assume you have the peak performance and bandwidth of your machine
# These should be measured or obtained from documentation
peak_flops = 500e9  # 500 GFLOPS for example
peak_bandwidth = 100e9  # 100 GB/s for example

# Function to measure the time taken by a numpy function
def measure_time(func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time

# List all numpy functions
numpy_functions = {name: func for name, func in np.__dict__.items() if callable(func)}

# Function to calculate operational intensity
def compute_intensity(func, args, flops, bytes_accessed):
    time_taken = measure_time(func, *args)
    return flops / bytes_accessed, flops / time_taken

# Classify the functions
classification = []
for name, func in numpy_functions.items():
    try:
        params = inspect.signature(func).parameters
        if len(params) == 1:
            sample_input = np.random.rand(1000000)
            flops = 2 * sample_input.size  # Simple estimation of operations
            bytes_accessed = sample_input.nbytes * 2  # Input and output
            intensity, performance = compute_intensity(func, (sample_input,), flops, bytes_accessed)
            if performance < (intensity * peak_bandwidth):
                classification.append((name, "Memory-bound"))
            else:
                classification.append((name, "Compute-bound"))
        else:
            continue
    except Exception as e:
        classification.append((name, f"Could not classify: {str(e)}"))

# Plot the results (optional)
compute_bound = [f[0] for f in classification if f[1] == "Compute-bound"]
memory_bound = [f[0] for f in classification if f[1] == "Memory-bound"]

plt.barh(compute_bound, [1] * len(compute_bound), color='blue', label='Compute-bound')
plt.barh(memory_bound, [1] * len(memory_bound), color='red', label='Memory-bound')
plt.xlabel("Classifications")
plt.ylabel("NumPy Functions")
plt.title("Roofline Analysis of NumPy Functions")
plt.legend()
plt.show()

# Print the results
for func_name, class_type in classification:
    print(f"Function: {func_name}, Classification: {class_type}")
