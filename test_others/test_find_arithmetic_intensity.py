import numpy as np
import inspect
import time

def measure_time_and_operations(func, *args, **kwargs):
    """Measures execution time and returns a rough estimate of FLOPs (floating-point operations)"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Estimate the number of floating-point operations (FLOPs)
    if func.__name__ in ["dot", "matmul"]:
        flops = 2 * args[0].shape[0] * args[0].shape[1] * args[1].shape[1]
    elif func.__name__ in ["add", "subtract", "multiply", "divide"]:
        flops = args[0].size
    else:
        flops = args[0].size  # Simple estimation for other operations
    
    return time_taken, flops, result

def memory_bytes_accessed(array_list):
    """Estimates the memory bytes accessed for a given list of arrays"""
    return sum(array.nbytes for array in array_list)

def compute_arithmetic_intensity(func, *args):
    time_taken, flops, result = measure_time_and_operations(func, *args)
    bytes_accessed = memory_bytes_accessed(args)
    
    if isinstance(result, np.ndarray):
        bytes_accessed += result.nbytes
    
    if bytes_accessed > 0:
        intensity = flops / bytes_accessed
    else:
        intensity = float('inf')
    
    return intensity

# List of numpy functions to analyze
numpy_functions = {
    "dot": np.dot,
    "add": np.add,
    "subtract": np.subtract,
    "multiply": np.multiply,
    "divide": np.divide,
    "matmul": np.matmul,
    "exp": np.exp,
    "log": np.log,
    "sin": np.sin,
    "cos": np.cos
}

# Test the arithmetic intensity of each function
results = {}
for name, func in numpy_functions.items():
    try:
        if func.__name__ in ["dot", "matmul"]:
            A = np.random.rand(1000, 1000)
            B = np.random.rand(1000, 1000)
            intensity = compute_arithmetic_intensity(func, A, B)
        else:
            A = np.random.rand(1000000)
            B = np.random.rand(1000000)
            intensity = compute_arithmetic_intensity(func, A, B)
        
        results[name] = intensity
        print(f"Function: {name}, Arithmetic Intensity: {intensity:.6f} FLOPs/byte")
    except Exception as e:
        print(f"Could not compute for {name}: {str(e)}")

# Print out all results
print("\nArithmetic Intensity Results:")
for func_name, intensity in results.items():
    print(f"{func_name}: {intensity:.6f} FLOPs/byte")
