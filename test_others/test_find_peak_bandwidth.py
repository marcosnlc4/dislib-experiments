import numpy as np
import time

# Function to measure peak memory bandwidth
def measure_memory_bandwidth():
    n = 10**8  # Size of array (800 MB for float64)
    a = np.random.rand(n)
    
    # Warm-up phase (not timed)
    b = np.copy(a)
    
    # Time the copy operation
    start_time = time.time()
    b = np.copy(a)
    end_time = time.time()
    
    # Calculate the bandwidth
    bytes_transferred = a.nbytes + b.nbytes  # a -> b copy means 2x the size
    time_taken = end_time - start_time
    bandwidth = bytes_transferred / time_taken  # Bytes per second
    
    print(f"Peak Memory Bandwidth: {bandwidth / 1e9:.2f} GB/s")

# Function to measure peak compute performance (FLOPS)
def measure_compute_bandwidth():
    n = 4096  # Size of matrix (4096x4096)
    a = np.random.rand(n, n)
    b = np.random.rand(n, n)
    
    # Warm-up phase (not timed)
    c = np.dot(a, b)
    
    # Time the matrix multiplication operation
    start_time = time.time()
    c = np.dot(a, b)
    end_time = time.time()
    
    # Calculate the FLOPS
    flops = 2 * n**3  # 2*n^3 operations for matrix multiplication
    time_taken = end_time - start_time
    gflops = flops / time_taken / 1e9  # GigaFLOPS
    
    print(f"Peak Compute Bandwidth: {gflops:.2f} GFLOPS")

# Measure both
measure_memory_bandwidth()
measure_compute_bandwidth()
