import dask.array as da
from dask.distributed import Client, wait
from dask_cuda import LocalCUDACluster
from cuml.dask.cluster import KMeans as cuMLKMeans
from sklearn.datasets import make_blobs
import cupy as cp

# Create sample data
n_samples = 10000
n_features = 50
n_clusters = 5
X, _ = make_blobs(n_samples=n_samples, n_features=n_features, centers=n_clusters, random_state=42)

# Convert sample data to Dask array
X_dask = da.from_array(X, chunks=(1000, n_features))

# Initialize a Dask client for CPU execution
client_cpu = Client()

# Execution Plan: CPU Cold
# Run KMeans without persisting data
kmeans_cpu_cold = cuMLKMeans(n_clusters=n_clusters)
kmeans_cpu_cold_fit = kmeans_cpu_cold.fit(X_dask)
labels_cpu_cold = kmeans_cpu_cold.labels_.compute()

# Visualize the DAG for CPU Cold
kmeans_cpu_cold_fit.visualize(filename='cpu_cold_dag.svg')

# Execution Plan: CPU Hot
# Persist data in CPU memory
X_dask_cpu_cached = X_dask.persist()
wait(X_dask_cpu_cached)  # Ensure data is cached
kmeans_cpu_hot = cuMLKMeans(n_clusters=n_clusters)
kmeans_cpu_hot_fit = kmeans_cpu_hot.fit(X_dask_cpu_cached)
labels_cpu_hot = kmeans_cpu_hot.labels_.compute()

# Visualize the DAG for CPU Hot
kmeans_cpu_hot_fit.visualize(filename='cpu_hot_dag.svg')

# Initialize a Dask client for GPU execution
cluster = LocalCUDACluster()
client_gpu = Client(cluster)

# Convert data to CuPy arrays for GPU processing
X_dask_gpu = da.from_array(cp.asarray(X), chunks=(1000, n_features))

# Execution Plan: GPU Cold
# Run KMeans without persisting data
kmeans_gpu_cold = cuMLKMeans(n_clusters=n_clusters)
kmeans_gpu_cold_fit = kmeans_gpu_cold.fit(X_dask_gpu)
labels_gpu_cold = kmeans_gpu_cold.labels_.compute()

# Visualize the DAG for GPU Cold
kmeans_gpu_cold_fit.visualize(filename='gpu_cold_dag.svg')

# Execution Plan: GPU Hot
# Persist data in GPU memory
X_dask_gpu_cached = X_dask_gpu.persist()
wait(X_dask_gpu_cached)  # Ensure data is cached
kmeans_gpu_hot = cuMLKMeans(n_clusters=n_clusters)
kmeans_gpu_hot_fit = kmeans_gpu_hot.fit(X_dask_gpu_cached)
labels_gpu_hot = kmeans_gpu_hot.labels_.compute()

# Visualize the DAG for GPU Hot
kmeans_gpu_hot_fit.visualize(filename='gpu_hot_dag.svg')

# Print results for verification
print("CPU Cold Labels:", labels_cpu_cold[:10])
print("CPU Hot Labels:", labels_cpu_hot[:10])
print("GPU Cold Labels:", labels_gpu_cold[:10])
print("GPU Hot Labels:", labels_gpu_hot[:10])

# Shutdown clients
client_cpu.shutdown()
client_gpu.shutdown()
