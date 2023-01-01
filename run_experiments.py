import csv
import os
import time
import datetime
import pandas as pd
from sklearn.datasets import make_blobs

import dislib as ds
from dislib.cluster import KMeans
from dislib.data.array import Array

from pycompss.api.api import compss_barrier

def main():
    # Path of the "tb_parameters" table - CSV file
    src_path_parameters = "experiments/parameters/tb_parameters.csv"
    # Path of the "tb_experiments" table - CSV file
    dst_path_experiments = "experiments/results/tb_experiments_raw.csv"

    # Reading "tb_parameters" table
    param_file = os.path.join(src_path_parameters)
    df_parameters = pd.read_csv(param_file)

    # # Filtering and sorting parameters
    # df_parameters = df_parameters[
    #                                 (df_parameters["ds_algorithm"] == "KMEANS") # FIXED VALUE
    #                                 & (df_parameters["nr_iterations"] == 5) # FIXED VALUE
    #                                 & (df_parameters["ds_resource"] == "MINOTAURO_2") # FIXED VALUE
    #                                 # & (df_parameters["ds_dataset"] == "S_AA_1" | df_parameters["ds_dataset"] == "S_AA_2" | df_parameters["ds_dataset"] == "S_AA_3" | df_parameters["ds_dataset"] == "S_AA_4" | df_parameters["ds_dataset"] == "S_BB_1" | df_parameters["ds_dataset"] == "S_BB_2" | df_parameters["ds_dataset"] == "S_BB_3" | df_parameters["ds_dataset"] == "S_BB_4" | df_parameters["ds_dataset"] == "S_CC_1" | df_parameters["ds_dataset"] == "S_CC_2" | df_parameters["ds_dataset"] == "S_CC_3" | df_parameters["ds_dataset"] == "S_CC_4") # FIXED VALUE
    #                                 # & (df_parameters["ds_dataset"].isin(["S_A_1","S_A_2","S_A_3","S_A_4","S_B_1","S_B_2","S_B_3","S_B_4","S_C_1","S_C_2","S_C_3","S_C_4"])) # FIXED VALUE
    #                                 & (df_parameters["ds_dataset"].isin(["S_AA_1","S_AA_2","S_AA_3","S_AA_4","S_BB_1","S_BB_2","S_BB_3","S_BB_4","S_CC_1","S_CC_2","S_CC_3","S_CC_4"])) # FIXED VALUE
    #                                 & (df_parameters["ds_parameter_type"] == "VAR_BLOCK_CAPACITY_SIZE") # 1.1, 1.2, 1.3, 1.4
    #                                 # & (df_parameters["ds_parameter_type"] == "VAR_PARALLELISM_LEVEL") # 2.1, 2.2
    #                                 # & (df_parameters["ds_parameter_attribute"] == "0.25") # 1.1
    #                                 # & (df_parameters["ds_parameter_attribute"] == "0.50") # 1.2
    #                                 # & (df_parameters["ds_parameter_attribute"] == "0.75") # 1.3
    #                                 # & (df_parameters["ds_parameter_attribute"] == "1.00") # 1.4
    #                                 # & (df_parameters["ds_parameter_attribute"] == "MIN_INTER_MAX_INTRA") # 2.1
    #                                 # & (df_parameters["ds_parameter_attribute"] == "MAX_INTER_MIN_INTRA") # 2.2
    #                                 # & (df_parameters["vl_dataset_memory_size"] == 400) # 2.2.1
    #                                 # & (df_parameters["vl_dataset_memory_size"] == 400000) # 2.2.2
    #                                 # & (df_parameters["vl_dataset_memory_size"] == 400000000) # 2.2.3
    #                                 # & (df_parameters["vl_dataset_memory_size"] == 640) # 2.2.1
    #                                 # & (df_parameters["vl_dataset_memory_size"] == 640000) # 2.2.2
    #                                 & (df_parameters["vl_dataset_memory_size"] != 640000000) # 2.2.3
    #                             ].sort_values(by=["id_parameter"])


    # # Filtering and sorting parameters V2
    # df_parameters = df_parameters[
    #                                  (df_parameters["ds_algorithm"] == "KMEANS") # FIXED VALUE
    #                                  & (df_parameters["nr_iterations"] == 5) # FIXED VALUE
    #                                  # & (df_parameters["ds_dataset"].isin(["S_10MB_1","S_100MB_1","S_1GB_1","S_10GB_1"])) # FIXED VALUE
    #                                  & (df_parameters["ds_dataset"] == "S_1GB_1")
    #                                  & (df_parameters["ds_resource"] == "MINOTAURO_9_NODES_16_CORES")
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_ROW") # 1
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_COLUMN") # 2
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_ROW_2") # 1.1
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_ROW_3") # 1.2
    #                                  & (df_parameters["ds_parameter_type"] == "VAR_GRID_ROW_4") # 1.3
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_CORES_CLUSTER_2") # 2.1
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_CORES_CLUSTER_3") # 2.2
    #                                 #  & (df_parameters["ds_parameter_type"] == "VAR_CORES_CLUSTER_4") # 2.3
    #                              ].sort_values(by=["id_parameter"])

    # # Filtering and sorting parameters V3
    # df_parameters = df_parameters[
    #                                 (df_parameters["ds_algorithm"] == "KMEANS") # FIXED VALUE
    #                                 & (df_parameters["nr_iterations"] == 5) # FIXED VALUE
    #                                 & (df_parameters["ds_dataset"] == "S_10GB_1")
    #                                 & (df_parameters["ds_parameter_type"] == "VAR_CORES_CLUSTER_1") # 1
    #                                 & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_3_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_4_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_5_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_6_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_7_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_8_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_9_NODES_16_CORES") # 1
    #                                 # & (df_parameters["ds_parameter_type"] == "VAR_CORES_SINGLE_NODE_1") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_2_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_4_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_6_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_8_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_10_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_12_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_14_CORES") # 2
    #                                 # & (df_parameters["ds_resource"] == "MINOTAURO_2_NODES_16_CORES") # 2
    #                             ].sort_values(by=["id_parameter"])

    # Filtering and sorting parameters (TEST)
    # df_parameters = df_parameters[(df_parameters["id_parameter"] != 11832) & (df_parameters["id_parameter"] != 11830) & (df_parameters["id_parameter"] != 11828) & (df_parameters["id_parameter"] != 11827) & (df_parameters["id_parameter"] != 11826) & (df_parameters["id_parameter"] != 11825)].sort_values(by=["id_parameter"])
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 11841) | (df_parameters["id_parameter"] == 11842)]
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 7531)]

    # Filtering and sorting parameters (MATMUL_DISLIB)
    df_parameters = df_parameters[
                                     (df_parameters["ds_algorithm"] == "MATMUL_DISLIB") # FIXED VALUE
                                     & ((df_parameters["cd_configuration"] == 1) | (df_parameters["cd_configuration"] == 4)) # FIXED VALUE
                                     & (df_parameters["nr_iterations"] == 5) # FIXED VALUE
                                     & ((df_parameters["id_function"] == 1) | (df_parameters["id_function"] == 2)) # FIXED VALUE (gpu version is called inside task, as matmul has two device functions (matmul and add))  
                                    #  & (df_parameters["ds_dataset"].isin(["S_128MB_1","S_512MB_1","S_2GB_1","S_8GB_1","S_32GB_1"])) # FIXED VALUE
                                     & (df_parameters["ds_dataset"] == "S_128MB_1") #1
                                    #  & (df_parameters["ds_dataset"] == "S_512MB_1") #2
                                    #  & (df_parameters["ds_dataset"] == "S_2GB_1") #3
                                    #  & (df_parameters["ds_dataset"] == "S_8GB_1") #4
                                    #  & (df_parameters["ds_dataset"] == "S_32GB_1") #5
                                     & (df_parameters["ds_resource"] == "MINOTAURO_9_NODES_1_CORE")
                                     & (df_parameters["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_1") # 1 (NO TRANSPOSE - GPFS - es.bsc.compss.scheduler.orderstrict.fifo.FifoTS)
                                    #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_2") # 2 (NO TRANSPOSE - LOCAL DISK - es.bsc.compss.scheduler.lookahead.successors.fifolocality.FifoLocalityTS)
                                    #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_3") # 3 (TRANSPOSE - GPFS - es.bsc.compss.scheduler.orderstrict.fifo.FifoTS)
                                    #  & (df_parameters["ds_parameter_type"] == "VAR_GRID_SHAPE_MATMUL_4") # 4 (TRANSPOSE - LOCAL DISK - es.bsc.compss.scheduler.lookahead.successors.fifolocality.FifoLocalityTS)
                                 ].sort_values(by=["id_parameter"])
    # df_parameters = df_parameters[(df_parameters["id_parameter"] == 5) | (df_parameters["id_parameter"] == 7)]


    # defining the structure of the log file
    header = ["id_parameter", "nr_algorithm_iteration", "nr_function_iteration", "nr_task", "start_total_execution_time", "end_total_execution_time", "start_inter_time_cpu", "end_inter_time_cpu", "intra_task_execution_full_func", "vl_intra_task_execution_time_device_func", "start_communication_time_1", "end_communication_time_1", "start_communication_time_2", "end_communication_time_2", "start_additional_time_1", "end_additional_time_1", "start_additional_time_2", "end_additional_time_2", "dt_processing"]
    # header = ["id_parameter", "nr_algorithm_iteration", "nr_function_iteration", "nr_task", "vl_total_execution_time", "vl_inter_task_execution_time", "vl_intra_task_execution_time_full_func", "vl_intra_task_execution_time_device_func", "vl_communication_time_1", "vl_communication_time_2", "vl_additional_time_1", "vl_additional_time_2", "dt_processing"]
    # open the log file in the write mode
    f = open(dst_path_experiments, "w", encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close()

    # Variable to store the current execution to measure the progress of the experiment
    current_execution = 0

    # Iterate over each row of the parameter table CSV file
    for index, row in df_parameters.iterrows():

        current_execution += 1

        # Setting parameters variables
        # parameter = set_parameter_object()

        id_parameter = row["id_parameter"]
        cd_parameter = row["cd_parameter"]
        cd_configuration = row["cd_configuration"]
        id_algorithm = row["id_algorithm"]
        ds_algorithm = row["ds_algorithm"]
        id_function = row["id_function"]
        ds_function = row["ds_function"]
        id_device = row["id_device"]
        ds_device = row["ds_device"]
        id_dataset = row["id_dataset"]
        id_resource = row["id_resource"]
        id_parameter_type = row["id_parameter_type"]
        ds_parameter_type = row["ds_parameter_type"]
        ds_parameter_attribute = row["ds_parameter_attribute"]
        ds_compss_version = row["ds_compss_version"]
        ds_dislib_version = row["ds_dislib_version"]
        ds_schdeuler = row["ds_schdeuler"]
        nr_cluster = row["nr_cluster"]
        bl_transpose_matrix = row["bl_transpose_matrix"]
        nr_iterations = row["nr_iterations"]
        vl_grid_row_dimension = row["vl_grid_row_dimension"]
        vl_grid_column_dimension = row["vl_grid_column_dimension"]
        vl_block_row_dimension = row["vl_block_row_dimension"]
        vl_block_column_dimension = row["vl_block_column_dimension"]
        vl_block_memory_size = row["vl_block_memory_size"]
        vl_block_memory_size_percent_cpu = row["vl_block_memory_size_percent_cpu"]
        vl_block_memory_size_percent_gpu = row["vl_block_memory_size_percent_gpu"]
        ds_resource = row["ds_resource"]
        nr_nodes = row["nr_nodes"]
        nr_computing_units_cpu = row["nr_computing_units_cpu"]
        nr_computing_units_gpu = row["nr_computing_units_gpu"]
        vl_memory_size_per_cpu_computing_unit = row["vl_memory_size_per_cpu_computing_unit"]
        vl_memory_size_per_gpu_computing_unit = row["vl_memory_size_per_gpu_computing_unit"]
        ds_dataset = row["ds_dataset"]
        vl_dataset_memory_size = row["vl_dataset_memory_size"]
        ds_data_type = row["ds_data_type"]
        vl_data_type_memory_size = row["vl_data_type_memory_size"]
        vl_dataset_dimension = row["vl_dataset_dimension"]
        vl_dataset_row_dimension = row["vl_dataset_row_dimension"]
        vl_dataset_column_dimension = row["vl_dataset_column_dimension"]
        nr_random_state = row["nr_random_state"]

        execution_progress = round((current_execution/df_parameters.shape[0])*100,2)
        print("\n@@@@@@ EXECUTION PROGRESS:",str(execution_progress),"%\n")
        print("nodes: ",str(nr_nodes),"\n")
        print("computing_units_cpu: ",str(nr_computing_units_cpu),"\n")
        print("vl_memory_size_per_cpu_computing_unit: ",str(vl_memory_size_per_cpu_computing_unit),"\n")
        print("computing_units_gpu: ",str(nr_computing_units_gpu),"\n")
        print("vl_memory_size_per_gpu_computing_unit: ",str(vl_memory_size_per_gpu_computing_unit),"\n")
        print("ds_device: ",str(ds_device),"\n")
        print("ds_parameter_type: ",str(ds_parameter_type),"\n")
        print("ds_parameter_type: ",str(ds_parameter_type),"\n")
        print("vl_dataset_memory_size: ",str(vl_dataset_memory_size),"\n")
        print("DATASET: vl_dataset_row_size x vl_dataset_column_size: ",str(vl_dataset_row_dimension)," x ",str(vl_dataset_column_dimension),"\n")
        print("GRID: vl_grid_row_size x vl_grid_column_size: ",str(vl_grid_row_dimension)," x ",str(vl_grid_column_dimension),"\n")
        print("BLOCK: vl_block_row_size x vl_block_column_size: ",str(vl_block_row_dimension)," x ",str(vl_block_column_dimension),"\n")
        print("vl_block_memory_size: ",str(vl_block_memory_size),"\n")
        print("vl_block_memory_size_percent_cpu: ",str(vl_block_memory_size_percent_cpu*100),"%\n")
        print("vl_block_memory_size_percent_gpu: ",str(vl_block_memory_size_percent_gpu*100),"%\n")

        # Execute the experiment for N (nr_iterations) times with the same parameter set
        for i in range(nr_iterations + 1):
            
            iteration_experiment_time_start = datetime.datetime.now()

            print("\nEXPERIMENT ", id_parameter,"-------------- ITERATION ", i, " STARTED AT "+str(iteration_experiment_time_start)+"------------------\n")

            if ds_algorithm == "KMEANS":

                # generate and load data into a ds-array
                dis_x = ds.random_array((vl_dataset_row_dimension, vl_dataset_column_dimension), (vl_block_row_dimension, vl_block_column_dimension), random_state=nr_random_state)
                
                if ds_device == "GPU":

                    # execution 1 - extract intra execution times with CUDA events
                    kmeans = KMeans(n_clusters=nr_cluster, random_state=nr_random_state, id_device=4, id_parameter=id_parameter, nr_algorithm_iteration=i, max_iter=5, tol=0, arity=48)
                    kmeans.fit(dis_x)

                    # execution 2 - extract total and inter execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=nr_cluster, random_state=nr_random_state, id_device=6, id_parameter=id_parameter, nr_algorithm_iteration=i, max_iter=5, tol=0, arity=48)
                    kmeans.fit(dis_x)

                else:

                    # execution 1 - extract intra execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=nr_cluster, random_state=nr_random_state, id_device=3, id_parameter=id_parameter, nr_algorithm_iteration=i, max_iter=5, tol=0, arity=48)
                    kmeans.fit(dis_x)

                    # execution 2 - extract total and inter execution times with synchornized function calls
                    kmeans = KMeans(n_clusters=nr_cluster, random_state=nr_random_state, id_device=5, id_parameter=id_parameter, nr_algorithm_iteration=i, max_iter=5, tol=0, arity=48)
                    kmeans.fit(dis_x)

                # # execution 3 - extract total execution time for CPU (id_device = 1) and GPU (id_device = 2)
                # compss_barrier()
                # start_total_execution_time = time.perf_counter()
                # kmeans = KMeans(n_clusters=nr_cluster, random_state=nr_random_state, id_device=id_device, max_iter=5, tol=0, arity=48)
                # kmeans.fit(dis_x)
                # compss_barrier()
                # end_total_execution_time = time.perf_counter()

                # # log total execution time
                # total_execution_time = end_total_execution_time - start_total_execution_time

                # # open the log file in the append mode
                # f = open(dst_path_experiments, "a", encoding='UTF8', newline='')

                # # create a csv writer
                # writer = csv.writer(f)

                # # write the time data 
                # var_null = 'NULL'
                # data = [id_parameter, i, var_null, var_null, total_execution_time, var_null, var_null, var_null, var_null, var_null, var_null, var_null, datetime.datetime.now()]
                # writer.writerow(data)
                # f.close()


            elif ds_algorithm == "MATMUL_DISLIB":

                # generate and load data into a ds-array
                x = ds.random_array((vl_dataset_row_dimension, vl_dataset_column_dimension), (vl_block_row_dimension, vl_block_column_dimension), random_state=nr_random_state)

                transpose_a = transpose_b = bl_transpose_matrix

                if ds_device == "GPU":

                    # execution 1 - extract intra execution times with CUDA events
                    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=4, id_parameter=id_parameter, nr_algorithm_iteration=i)

                    # execution 2 - extract total and inter execution times with synchornized function calls
                    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=6, id_parameter=id_parameter, nr_algorithm_iteration=i)

                    # # execution 3 - extract total execution time for GPU (id_device = 2)
                    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=2, id_parameter=id_parameter, nr_algorithm_iteration=i)
                else:

                    # execution 1 - extract intra execution times with synchornized function calls
                    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=3, id_parameter=id_parameter, nr_algorithm_iteration=i)

                    # execution 2 - extract total and inter execution times with synchornized function calls
                    result = ds.matmul(x, x, transpose_a, transpose_b, id_device=5, id_parameter=id_parameter, nr_algorithm_iteration=i)

                    # # execution 3 - extract total execution time for CPU (id_device = 1)
                    # result = ds.matmul(x, x, transpose_a, transpose_b, id_device=1, id_parameter=id_parameter, nr_algorithm_iteration=i)

            else:
                print("Invalid Algorithm!")
            
            iteration_experiment_time_end = datetime.datetime.now()
            iteration_experiment_time = (iteration_experiment_time_end - iteration_experiment_time_start).total_seconds()
            print("\nEXPERIMENT ", index+1,"-------------- ITERATION ", i, " FINISHED AT "+str(iteration_experiment_time_end)+" (TOTAL TIME: "+str(iteration_experiment_time)+") ------------------\n")

if __name__ == "__main__":
    main()