# # TEST USING K-MEANS
# import time

# import dislib as ds
# import numpy as np
# from dislib.cluster import KMeans

# from pycompss.api.api import compss_barrier
# from pycompss.api.api import compss_wait_on

# if __name__ == '__main__':

# # # CLEAN CODE (FOR TRACE GENERATION)
#     input_matrix_rows = 8
#     input_matrix_columns = 4
#     start_random_state = 170
#     vl_data_skewness = 0.0
#     block_row_size = 4
#     block_column_size = 2
#     n_clusters = 10

#     shape = (input_matrix_rows, input_matrix_columns)
#     block_size = (block_row_size, block_column_size)

#     start = time.perf_counter()
#     x = ds.random_array(shape, block_size, random_state=start_random_state, data_skewness=vl_data_skewness)
#     print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)
#     # arr = np.random.rand(input_matrix_rows, input_matrix_columns)
#     # x = ds.array(arr, block_size=(block_row_size, block_column_size))
    
#     # x_np = np.random.random(shape)
#     # x = ds.array(x_np, block_size=block_size)
#     time_arr = np.array([])
#     nr_iterations = 0
    
#     for i in range(nr_iterations + 1):

#         # Run KMeans using dislib - CPU
#         print("\nSTART CPU\n")
#         compss_barrier()
#         start = time.perf_counter()
#         kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=1, max_iter=5, tol=0, arity=48)
#         kmeans.fit(x)
#         compss_barrier()
#         print("==== TIME CPU ==== ", time.perf_counter()-start)
#         time_arr = np.append(time_arr,time.perf_counter()-start)
#         print("\END CPU\n")

#     print('Average time : ', np.mean(time_arr))

#     xx = compss_wait_on(x)
#     print(xx.collect())
#         # # Run KMeans using dislib - GPU
#         # print("\nSTART GPU\n")
#         # compss_barrier()
#         # start = time.perf_counter()
#         # kmeans = KMeans(n_clusters=n_clusters, random_state=start_random_state, id_device=2, max_iter=5, tol=0, arity=48)
#         # kmeans.fit(x)
#         # compss_barrier()
#         # print("==== TIME GPU ==== ", time.perf_counter()-start)








# #MULTIDIMENSIONAL ARRAY USING np.random.random
# import numpy as np
# import matplotlib.pyplot as plt

# def generate_skewed_array(shape=(1000,), skew_percentage=0.20):
#     """
#     Generate a random skewed NumPy array with a specified shape.

#     Parameters:
#     - shape: Tuple representing the shape of the array.
#     - skew_percentage: Skewness parameter in percentage.

#     Returns:
#     - skewed_array: NumPy array with skewed values.
#     """
#     # Generate a random array with the specified shape
#     random_array = np.random.random(shape)

#     # Calculate the skewness threshold
#     skew_threshold = np.percentile(random_array, skew_percentage*100)

#     # Apply skewness using a threshold
#     skewed_array = np.where(random_array < skew_threshold, random_array * 0.5, random_array)

#     return skewed_array

# # Example usage
# rows = 1000
# cols = 3
# shape = (rows,cols)
# skew_percentage = 0.0

# skewed_array = generate_skewed_array(shape, skew_percentage)

# # Scatter plot of the skewed NxM array (for visualization in 3D)
# if cols == 3:
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     ax.scatter(skewed_array[:, 0], skewed_array[:, 1], skewed_array[:, 2], alpha=0.7, edgecolors='black', s=25)
#     ax.set_title('Non-Skewed NxM NumPy Array')
#     ax.set_xlabel('Dimension 1')
#     ax.set_ylabel('Dimension 2')
#     ax.set_zlabel('Dimension 3')
#     plt.show()
# else:
#     print("Visualization is supported for 3D arrays only.")
#     print(skewed_array)









# MULTIDIMENSIONAL ARRAY USING np.random.rand
import numpy as np
import matplotlib.pyplot as plt

def generate_skewed_nxm_array(rows=1000, cols=2, skew_percentage=0.2):
    """
    Generate a random skewed NxM NumPy array.

    Parameters:
    - rows: Number of rows in the array.
    - cols: Number of columns in the array.
    - skew_percentage: Skewness parameter in percentage.

    Returns:
    - skewed_array: NxM NumPy array with skewed values.
    """
    # Generate a random NxM array
    random_array = np.random.rand(rows, cols)

    # Calculate the skewness threshold for each column
    skew_thresholds = [np.percentile(random_array[:, i], skew_percentage*100) for i in range(cols)]
    print(random_array)
    # Apply skewness using a threshold for each column
    skewed_array = np.column_stack([
        np.where(random_array[:, i] < skew_thresholds[i], random_array[:, i] * 0.5, random_array[:, i])
        for i in range(cols)
    ])

    return skewed_array

# Example usage
rows = 1000
cols = 2
skew_percentage = 1.00

skewed_nxm_array = generate_skewed_nxm_array(rows, cols, skew_percentage)
print('HERE')
print(skewed_nxm_array)

# Scatter plot of the skewed NxM array (for visualization in 3D)
if cols == 3:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(skewed_nxm_array[:, 0], skewed_nxm_array[:, 1], skewed_nxm_array[:, 2], alpha=0.7, edgecolors='black', s=25)
    ax.set_title('Skewed NumPy Array')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    ax.set_zlabel('Dimension 3')
    plt.show()
elif cols == 2:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(skewed_nxm_array[:, 0], skewed_nxm_array[:, 1], alpha=0.7, edgecolors='black', s=25)
    ax.set_title('NumPy Array (Skewness 100%)')
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    plt.show()
else:
    print("Visualization is supported for 2D arrays only.")

# For 2D arrays, you can visualize using a scatter plot similar to the previous examples









# # 2D ARRAY USING np.random.rand
# import numpy as np
# import matplotlib.pyplot as plt

# def generate_skewed_array(size=1000, skew_percentage=0.2):
#     """
#     Generate a random skewed NumPy array.

#     Parameters:
#     - size: Number of elements in the array.
#     - skew_percentage: Skewness parameter in percentage.

#     Returns:
#     - skewed_array: NumPy array with skewed values.
#     """
#     # Generate a random array
#     random_array = np.random.rand(size)

#     # Calculate the threshold for skewness
#     skew_threshold = np.percentile(random_array, skew_percentage*100)

#     # Apply skewness using a threshold
#     skewed_array = np.where(random_array < skew_threshold, random_array * 0.5, random_array)

#     return skewed_array

# # Example usage
# size = 1000
# skew_percentage = 0.0

# skewed_array = generate_skewed_array(size, skew_percentage)

# # Plot the histogram of the skewed array
# plt.hist(skewed_array, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')
# plt.title('Skewed NumPy Array')
# plt.xlabel('Values')
# plt.ylabel('Density')
# plt.show()






















