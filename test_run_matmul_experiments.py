import time
import csv
import dislib as ds
import numpy as np
from scipy import sparse as sp
from scipy.sparse import csr_matrix

from pycompss.api.api import compss_barrier

if __name__ == '__main__':

    dst_path_experiments = "experiments/results/tb_experiments_raw.csv"
    # defining the structure of the log file
    header = ["id_parameter", "nr_algorithm_iteration", "nr_function_iteration", "nr_task", "start_total_execution_time", "end_total_execution_time", "start_inter_time_cpu", "end_inter_time_cpu", "intra_task_execution_full_func", "vl_intra_task_execution_time_device_func", "start_communication_time_1", "end_communication_time_1", "start_communication_time_2", "end_communication_time_2", "start_additional_time_1", "end_additional_time_1", "start_additional_time_2", "end_additional_time_2", "dt_processing"]
    # header = ["id_parameter", "nr_algorithm_iteration", "nr_function_iteration", "nr_task", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_full_func", "vl_intra_task_execution_time_device_func", "vl_communication_time_1", "vl_communication_time_2", "vl_additional_time_1", "vl_additional_time_2", "dt_processing"]
    # open the log file in the write mode
    f = open(dst_path_experiments, "w", encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()

    input_matrix_rows = 32000
    input_matrix_columns = 32000
    start_random_state = 170
    block_row_size = 16000
    block_column_size = 16000
    transpose_a = transpose_b = bl_transpose = False
    start = time.perf_counter()
    # x = ds.random_array((input_matrix_rows, input_matrix_columns), (block_row_size, block_column_size), random_state=start_random_state)
    
    shape = (input_matrix_rows, input_matrix_columns)
    block_size = (block_row_size, block_column_size)

    # # #DENSE
    # x_np = np.random.random(shape)
    # x = ds.array(x_np, block_size=block_size)

    #SPARSE
    # x_sp = sp.csr_matrix(np.random.random(shape))
    x_sp = csr_matrix(shape,dtype=np.float64).toarray()
    print(x_sp[0][0])
    print(type(x_sp[0][0]))
    x = ds.array(x_sp, block_size=block_size)


    # print(x.collect())

    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    # Run Matmul using dislib - CPU (Warm up)
    print("\nSTART CPU\n")
    # compss_barrier()
    start = time.perf_counter()
    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=0, nr_algorithm_iteration=0)
    # compss_barrier()
    print("==== TIME CPU ==== ", time.perf_counter()-start)







    # print(result.collect())

    # # Run KMeans using dislib - CPU - 3 (intra) - 5 (inter)
    # print("\nSTART CPU\n")
    # # compss_barrier()
    # start = time.perf_counter()
    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=5, id_parameter=0, nr_algorithm_iteration=0)
    # # compss_barrier()
    # print("==== TIME CPU ==== ", time.perf_counter()-start)

    # # Run KMeans using dislib - GPU (Warm up)
    # print("\nSTART GPU\n")
    # # compss_barrier()
    # start = time.perf_counter()
    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)
    # # compss_barrier()
    # print("==== TIME GPU ==== ", time.perf_counter()-start)

    # # Run KMeans using dislib - GPU - 4 (intra) - 6 (inter)
    # print("\nSTART GPU\n")
    # # compss_barrier()
    # start = time.perf_counter()
    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=6, id_parameter=0, nr_algorithm_iteration=0)
    # # compss_barrier()
    # print("==== TIME GPU ==== ", time.perf_counter()-start)













# # CLEAN CODE (FOR TRACE GENERATION)
# import time
# import csv
# import dislib as ds
# import numpy as np
# from scipy import sparse as sp
# from scipy.sparse import csr_matrix

# from pycompss.api.api import compss_barrier

# if __name__ == '__main__':


#     input_matrix_rows = 32000
#     input_matrix_columns = 32000
#     start_random_state = 170
#     block_row_size = 8000
#     block_column_size = 8000
#     transpose_a = transpose_b = bl_transpose = False
#     start = time.perf_counter()

#     shape = (input_matrix_rows, input_matrix_columns)
#     block_size = (block_row_size, block_column_size)

#     # DATASET GENERATION
#     x = ds.random_array(shape, block_size, random_state=start_random_state)

#     print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    
#     # Run Matmul using dislib - CPU
#     print("\nSTART CPU\n")
#     start = time.perf_counter()
#     result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=0, nr_algorithm_iteration=0)
#     print("==== TIME CPU ==== ", time.perf_counter()-start)
    
    

#     # Run Matmul using dislib - GPU 
#     #print("\nSTART GPU\n")
#     #start = time.perf_counter()
#     #result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)
#     #print("==== TIME GPU ==== ", time.perf_counter()-start)