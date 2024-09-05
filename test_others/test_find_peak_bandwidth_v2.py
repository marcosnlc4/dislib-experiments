import numpy as np
import time

def measure_peak_compute_bandwidth():
    """Measure the peak compute bandwidth in Gops/sec."""
    sizes = [512, 1024, 2048, 4096]
    best_gflops = 0

    for size in sizes:
        A = np.random.rand(size, size).astype(np.float64)
        B = np.random.rand(size, size).astype(np.float64)

        start_time = time.time()
        np.dot(A, B)  # Matrix multiplication
        end_time = time.time()

        elapsed_time = end_time - start_time
        num_operations = 2 * (size ** 3)  # 2 * size^3 FLOPs for matrix multiplication
        gflops = num_operations / (elapsed_time * 1e9)
        best_gflops = max(best_gflops, gflops)

    return best_gflops

def measure_peak_memory_bandwidth():
    """Measure the peak memory bandwidth in Gops/sec."""
    sizes = [256 * 1024 * 1024, 512 * 1024 * 1024, 1024 * 1024 * 1024]  # 256MB, 512MB, 1GB
    best_gb_s = 0

    for size in sizes:
        A = np.random.rand(size // 8).astype(np.float64)  # Divide by 8 because np.float64 uses 8 bytes

        start_time = time.time()
        B = A + 1.0  # Simple memory-bound operation
        end_time = time.time()

        elapsed_time = end_time - start_time
        gb_s = (size / elapsed_time) / 1e9
        best_gb_s = max(best_gb_s, gb_s)

    # Convert GB/s to Gops/sec by assuming each memory operation is equivalent to 1 operation
    return best_gb_s

def main():
    peak_compute_bandwidth = measure_peak_compute_bandwidth()
    peak_memory_bandwidth = measure_peak_memory_bandwidth()

    print(f"Peak Compute Bandwidth: {peak_compute_bandwidth:.2f} Gops/sec")
    print(f"Peak Memory Bandwidth: {peak_memory_bandwidth:.2f} Gops/sec")

if __name__ == "__main__":
    main()
