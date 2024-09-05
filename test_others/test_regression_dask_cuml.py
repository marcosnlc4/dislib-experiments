import dask.array as da
from dask.distributed import Client, wait
from dask_cuda import LocalCUDACluster
from cuml.dask.linear_model import LinearRegression as cuMLLinearRegression
from sklearn.datasets import make_regression
import cupy as cp

# Create sample data
n_samples = 10000
n_features = 50
X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=0.1, random_state=42)

# Convert sample data to Dask array
X_dask = da.from_array(X, chunks=(1000, n_features))
y_dask = da.from_array(y, chunks=(1000,))

# Initialize a Dask client for CPU execution
client_cpu = Client()

# Execution Plan: CPU Cold
# Run Linear Regression without persisting data
lr_cpu_cold = cuMLLinearRegression()
lr_cpu_cold_fit = lr_cpu_cold.fit(X_dask, y_dask)
predictions_cpu_cold = lr_cpu_cold.predict(X_dask).compute()

# Visualize the DAG for CPU Cold
lr_cpu_cold_fit.visualize(filename='cpu_cold_dag_lr.svg')

# Execution Plan: CPU Hot
# Persist data in CPU memory
X_dask_cpu_cached = X_dask.persist()
y_dask_cpu_cached = y_dask.persist()
wait([X_dask_cpu_cached, y_dask_cpu_cached])  # Ensure data is cached
lr_cpu_hot = cuMLLinearRegression()
lr_cpu_hot_fit = lr_cpu_hot.fit(X_dask_cpu_cached, y_dask_cpu_cached)
predictions_cpu_hot = lr_cpu_hot.predict(X_dask_cpu_cached).compute()

# Visualize the DAG for CPU Hot
lr_cpu_hot_fit.visualize(filename='cpu_hot_dag_lr.svg')

# Initialize a Dask client for GPU execution
cluster = LocalCUDACluster()
client_gpu = Client(cluster)

# Convert data to CuPy arrays for GPU processing
X_dask_gpu = da.from_array(cp.asarray(X), chunks=(1000, n_features))
y_dask_gpu = da.from_array(cp.asarray(y), chunks=(1000,))

# Execution Plan: GPU Cold
# Run Linear Regression without persisting data
lr_gpu_cold = cuMLLinearRegression()
lr_gpu_cold_fit = lr_gpu_cold.fit(X_dask_gpu, y_dask_gpu)
predictions_gpu_cold = lr_gpu_cold.predict(X_dask_gpu).compute()

# Visualize the DAG for GPU Cold
lr_gpu_cold_fit.visualize(filename='gpu_cold_dag_lr.svg')

# Execution Plan: GPU Hot
# Persist data in GPU memory
X_dask_gpu_cached = X_dask_gpu.persist()
y_dask_gpu_cached = y_dask_gpu.persist()
wait([X_dask_gpu_cached, y_dask_gpu_cached])  # Ensure data is cached
lr_gpu_hot = cuMLLinearRegression()
lr_gpu_hot_fit = lr_gpu_hot.fit(X_dask_gpu_cached, y_dask_gpu_cached)
predictions_gpu_hot = lr_gpu_hot.predict(X_dask_gpu_cached).compute()

# Visualize the DAG for GPU Hot
lr_gpu_hot_fit.visualize(filename='gpu_hot_dag_lr.svg')

# Print results for verification
print("CPU Cold Predictions:", predictions_cpu_cold[:10])
print("CPU Hot Predictions:", predictions_cpu_hot[:10])
print("GPU Cold Predictions:", predictions_gpu_cold[:10])
print("GPU Hot Predictions:", predictions_gpu_hot[:10])

# Shutdown clients
client_cpu.shutdown()
client_gpu.shutdown()
