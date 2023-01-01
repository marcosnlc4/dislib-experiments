import time
import csv
import dislib as ds

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

    input_matrix_rows = 4
    input_matrix_columns = 4
    start_random_state = 170
    block_row_size = 2
    block_column_size = 2
    transpose_a = transpose_b = bl_transpose = True
    start = time.perf_counter()
    x = ds.random_array((input_matrix_rows, input_matrix_columns), (block_row_size, block_column_size), random_state=start_random_state)
    
    # print(x.collect())

    print("==== TIME DATA GENERATION ==== ", time.perf_counter()-start)

    # Run KMeans using dislib - CPU (Warm up)
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

    # Run KMeans using dislib - GPU (Warm up)
    print("\nSTART GPU\n")
    # compss_barrier()
    start = time.perf_counter()
    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=0, nr_algorithm_iteration=0)
    # compss_barrier()
    print("==== TIME GPU ==== ", time.perf_counter()-start)

    # # Run KMeans using dislib - GPU - 4 (intra) - 6 (inter)
    # print("\nSTART GPU\n")
    # # compss_barrier()
    # start = time.perf_counter()
    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=6, id_parameter=0, nr_algorithm_iteration=0)
    # # compss_barrier()
    # print("==== TIME GPU ==== ", time.perf_counter()-start)
